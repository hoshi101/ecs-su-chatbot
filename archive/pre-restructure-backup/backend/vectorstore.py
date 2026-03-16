import os
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import configuration
from backend.config import QDRANT_API_KEY, QDRANT_URL, QDRANT_COLLECTION_NAME, EMBED_MODEL, EMBED_DIMENSIONS


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