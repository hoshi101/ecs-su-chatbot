import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import configuration - Updated for new structure
from src.backend.core.config import QDRANT_API_KEY, QDRANT_URL, QDRANT_COLLECTION_NAME, EMBED_MODEL, EMBED_DIMENSIONS


class BGEEmbedder(Embeddings):
    """BGE-M3 embeddings wrapper for better multilingual retrieval"""

    def __init__(self, model_name: str = None):
        """Initialize BGE-M3 embeddings model."""
        model_name = model_name or EMBED_MODEL
        print(f"🤖 Loading BGE-M3 model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  # Use CPU for compatibility
            encode_kwargs={'normalize_embeddings': True}  # Normalize for better retrieval
        )
        print("✅ BGE-M3 model loaded successfully")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self.embeddings.embed_query(text)


# Initialize embeddings instance
embeddings = BGEEmbedder()

# Initialize Qdrant client
def _get_qdrant_client():
    """Get Qdrant client instance"""
    if not all([QDRANT_API_KEY, QDRANT_URL]):
        raise ValueError("QDRANT_API_KEY and QDRANT_URL must be set in environment variables")

    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)
        return client
    except Exception as e:
        raise Exception(f"Failed to connect to Qdrant: {str(e)}")


# --- Retriever (Compatible with existing interface) ---
def get_retriever():
    """Initializes and returns the Qdrant vector store retriever."""
    client = _get_qdrant_client()

    # Ensure the collection exists, create if not
    try:
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if QDRANT_COLLECTION_NAME not in collection_names:
            print(f"Creating new Qdrant collection: {QDRANT_COLLECTION_NAME}...")
            client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBED_DIMENSIONS,  # BGE-M3 embedding dimension
                    distance=Distance.COSINE
                )
            )
            print(f"Created new Qdrant collection: {QDRANT_COLLECTION_NAME}")
        else:
            print(f"Using existing Qdrant collection: {QDRANT_COLLECTION_NAME}")
    except Exception as e:
        print(f"Warning: Could not verify/create collection: {str(e)}")

    # Initialize vector store
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION_NAME,
        embedding=embeddings
    )

    return vectorstore.as_retriever()


# --- Function to add documents to the vector store (Compatible with existing interface) ---
def add_document_to_vectorstore(text_content: str):
    """
    Adds a single text document to the Qdrant vector store.
    Splits the text into chunks before embedding and upserting.
    """
    if not text_content:
        raise ValueError("Document content cannot be empty.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )

    # Create Langchain Document objects from the raw text
    documents = text_splitter.create_documents([text_content])

    print(f"Splitting document into {len(documents)} chunks for indexing...")

    # Get the vectorstore instance
    client = _get_qdrant_client()
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION_NAME,
        embedding=embeddings
    )

    # Add documents to the vector store
    vectorstore.add_documents(documents)
    print(f"Successfully added {len(documents)} chunks to Qdrant collection '{QDRANT_COLLECTION_NAME}'.")


# --- Additional utility function for batch processing ---
def add_documents_batch(documents: List, batch_size: int = 100):
    """
    Add multiple documents to the vector store in batches for better performance.
    """
    client = _get_qdrant_client()
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION_NAME,
        embedding=embeddings
    )

    total_docs = len(documents)
    print(f"📤 Uploading {total_docs} documents to Qdrant in batches of {batch_size}...")

    for i in range(0, total_docs, batch_size):
        batch = documents[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_docs + batch_size - 1) // batch_size

        print(f"📤 Uploading batch {batch_num}/{total_batches} ({len(batch)} documents)...")
        vectorstore.add_documents(batch)

    print("✅ All documents uploaded successfully!")


# --- Document Management Functions ---
def get_documents_by_metadata(filters: Dict[str, Any]) -> List[Dict]:
    """
    Query documents by metadata filters from Qdrant.

    Args:
        filters: Dictionary of metadata filters (e.g., {"file_name": "example.pdf"})

    Returns:
        List of dictionaries containing document information

    Example:
        # Get all PDF documents
        docs = get_documents_by_metadata({"source_type": "pdf"})

        # Get documents from API uploads
        docs = get_documents_by_metadata({"upload_source": "api"})
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    try:
        client = _get_qdrant_client()

        # Build Qdrant filter conditions
        must_conditions = []
        for key, value in filters.items():
            must_conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )

        # Query Qdrant with filters
        search_result = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            scroll_filter=Filter(must=must_conditions) if must_conditions else None,
            limit=1000,  # Maximum results per query
            with_payload=True,
            with_vectors=False
        )

        # Extract document information
        documents = []
        for point in search_result[0]:  # scroll returns tuple (points, next_page_offset)
            doc_info = {
                "id": point.id,
                "metadata": point.payload,
                "content_preview": point.payload.get("page_content", "")[:200] if "page_content" in point.payload else ""
            }
            documents.append(doc_info)

        print(f"✅ Retrieved {len(documents)} documents matching filters: {filters}")
        return documents

    except Exception as e:
        print(f"❌ Error querying documents: {str(e)}")
        raise Exception(f"Failed to query documents: {str(e)}")


def delete_documents_by_metadata(filters: Dict[str, Any]) -> int:
    """
    Delete documents matching metadata filters from Qdrant.

    Args:
        filters: Dictionary of metadata filters (e.g., {"file_name": "example.pdf"})

    Returns:
        Number of documents deleted

    Example:
        # Delete all documents from a specific file
        count = delete_documents_by_metadata({"file_name": "old_doc.pdf"})
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    try:
        client = _get_qdrant_client()

        # Build Qdrant filter conditions
        must_conditions = []
        for key, value in filters.items():
            must_conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )

        if not must_conditions:
            raise ValueError("Filters cannot be empty for deletion")

        # First, get the points to delete
        search_result = client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            scroll_filter=Filter(must=must_conditions),
            limit=10000,  # Get all matching documents
            with_payload=False,
            with_vectors=False
        )

        point_ids = [point.id for point in search_result[0]]
        deleted_count = len(point_ids)

        if deleted_count > 0:
            # Delete the points
            client.delete(
                collection_name=QDRANT_COLLECTION_NAME,
                points_selector=point_ids
            )
            print(f"✅ Deleted {deleted_count} documents matching filters: {filters}")
        else:
            print(f"⚠️  No documents found matching filters: {filters}")

        return deleted_count

    except Exception as e:
        print(f"❌ Error deleting documents: {str(e)}")
        raise Exception(f"Failed to delete documents: {str(e)}")


def get_collection_stats() -> Dict[str, Any]:
    """
    Get statistics about the document collection.

    Returns:
        Dictionary containing collection statistics including:
        - total_documents: Total number of document chunks
        - by_source_type: Count by document type (pdf, csv, json, txt, md)
        - by_upload_source: Count by upload method (bulk, api)

    Example:
        stats = get_collection_stats()
        print(f"Total documents: {stats['total_documents']}")
    """
    try:
        client = _get_qdrant_client()

        # Get collection info
        collection_info = client.get_collection(collection_name=QDRANT_COLLECTION_NAME)
        total_documents = collection_info.points_count

        # Get all documents with metadata (using scroll for efficiency)
        all_points = []
        offset = None
        batch_size = 1000

        while True:
            scroll_result = client.scroll(
                collection_name=QDRANT_COLLECTION_NAME,
                limit=batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            points, next_offset = scroll_result
            all_points.extend(points)

            if next_offset is None or len(points) == 0:
                break
            offset = next_offset

        # Aggregate statistics
        by_source_type = {}
        by_upload_source = {}

        for point in all_points:
            payload = point.payload

            # Count by source type
            source_type = payload.get("source_type", "unknown")
            by_source_type[source_type] = by_source_type.get(source_type, 0) + 1

            # Count by upload source
            upload_source = payload.get("upload_source", "unknown")
            by_upload_source[upload_source] = by_upload_source.get(upload_source, 0) + 1

        stats = {
            "total_documents": total_documents,
            "by_source_type": by_source_type,
            "by_upload_source": by_upload_source,
            "collection_name": QDRANT_COLLECTION_NAME
        }

        print(f"✅ Collection stats retrieved: {total_documents} total documents")
        return stats

    except Exception as e:
        print(f"❌ Error getting collection stats: {str(e)}")
        raise Exception(f"Failed to get collection stats: {str(e)}")