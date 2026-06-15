#!/usr/bin/env python3
"""
Document Processing Script for the department support chatbot.
Processes curated documents from the data/ folder and stores them in the Qdrant vector database.
Run this once before starting the chat application.

Usage:
    python process_documents.py

Make sure to set the following environment variables in your .env file:
- QDRANT_API_KEY
- QDRANT_URL
- GOOGLE_API_KEY (optional, for future features)
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from project root
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Import from our backend modules - Updated for new structure
from src.backend.core.config import (
    QDRANT_API_KEY,
    QDRANT_URL,
    QDRANT_COLLECTION_NAME,
    EMBED_DIMENSIONS,
    DOC_SOURCE_DIR,
    DOC_SUPPORTED_FORMATS
)
from src.backend.services.vectorstore import BGEEmbedder, add_documents_batch, document_exists
from src.backend.services.document_processor import DocumentProcessor


def init_qdrant():
    """Initialize Qdrant client with configured settings."""
    if not all([QDRANT_API_KEY, QDRANT_URL]):
        raise ValueError("QDRANT_API_KEY and QDRANT_URL must be set in .env file")

    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)
        print(f"✅ Connected to Qdrant: {QDRANT_URL}")
        return client
    except Exception as e:
        raise Exception(f"Qdrant connection failed: {str(e)}")


# Document processor instance
processor = DocumentProcessor()


def should_process_file(file_path: str) -> bool:
    """
    Keep ingestion focused on curated content and avoid raw scrape artifacts.
    """
    path = Path(file_path)
    path_str = path.as_posix()

    if "/raw/" in path_str:
        return False

    if path.name == "index.json":
        return False

    if "/data/web/clean/" in path_str and path.suffix.lower() == ".json":
        return False

    return True


def process_all_documents(data_path: str = None, reprocess_existing: bool = False) -> Tuple[List, dict]:
    """Process all documents in the data folder using DocumentProcessor."""
    data_path = data_path or DOC_SOURCE_DIR
    all_documents = []
    summary = {"processed_files": 0, "skipped_existing": 0, "failed_files": 0, "total_chunks": 0}

    if not os.path.exists(data_path):
        print(f"❌ Data folder '{data_path}' not found")
        return all_documents, summary

    # Count total files for progress tracking
    supported_extensions = tuple(f'.{ext}' for ext in DOC_SUPPORTED_FORMATS)
    total_files = 0
    for root, _, files in os.walk(data_path):
        for file in files:
            if file.lower().endswith(supported_extensions):
                file_path = os.path.join(root, file)
                if not should_process_file(file_path):
                    continue
                total_files += 1

    if total_files == 0:
        print("📁 No documents found in data folder")
        return all_documents, summary

    print(f"📁 Found {total_files} documents to process...")
    processed_count = 0

    # Process each file using DocumentProcessor
    for root, _, files in os.walk(data_path):
        for file in files:
            if not file.lower().endswith(supported_extensions):
                continue

            file_path = os.path.join(root, file)
            if not should_process_file(file_path):
                continue
            print(f"📄 Processing: {file}")

            try:
                file_hash = processor._compute_file_hash(file_path)
                if not reprocess_existing and document_exists(file_path, file_hash):
                    summary["skipped_existing"] += 1
                    print(f"⏭️  Skipping already indexed file: {file}")
                    continue

                # Use DocumentProcessor to process the file
                documents = processor.process_file(file_path, source="bulk")

                if documents:
                    all_documents.extend(documents)
                    processed_count += 1
                    summary["processed_files"] += 1
                    summary["total_chunks"] += len(documents)
                    print(f"✅ Processed {file} ({processed_count}/{total_files}) - {len(documents)} chunks")
                else:
                    print(f"⚠️  No content extracted from {file}")

            except Exception as e:
                summary["failed_files"] += 1
                print(f"❌ Error processing {file}: {str(e)}")
                continue

    print(f"🎉 Successfully processed {processed_count}/{total_files} documents")
    print(f"⏭️  Skipped already indexed documents: {summary['skipped_existing']}")
    print(f"📊 Total document chunks created in this run: {len(all_documents)}")
    return all_documents, summary


def create_collection_if_needed(client, collection_name: str):
    """Create Qdrant collection if it doesn't exist."""
    try:
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if collection_name not in collection_names:
            print(f"📚 Creating new collection: {collection_name}")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=EMBED_DIMENSIONS,  # BGE-M3 embedding dimension
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection: {collection_name}")
        else:
            print(f"📚 Using existing collection: {collection_name}")
        return True
    except Exception as e:
        print(f"❌ Collection creation error: {str(e)}")
        return False


def main():
    """Main processing function."""
    parser = argparse.ArgumentParser(description="Process documents into the ECS chatbot Qdrant collection.")
    parser.add_argument(
        "--reprocess-existing",
        action="store_true",
        help="Reprocess files even if they already exist in Qdrant."
    )
    args = parser.parse_args()

    print("🚀 Starting department support chatbot document processing...")
    print("=" * 60)

    try:
        # Initialize components
        print("🔧 Initializing components...")
        client = init_qdrant()

        # Create collection if needed
        if not create_collection_if_needed(client, QDRANT_COLLECTION_NAME):
            print("❌ Failed to create/access collection. Exiting.")
            return

        # Initialize embeddings (this will download BGE-M3 model if needed)
        print("🤖 Initializing BGE-M3 embeddings model...")
        embedder = BGEEmbedder()

        # Process documents
        print(f"\n📁 Processing documents from '{DOC_SOURCE_DIR}' folder...")
        documents, summary = process_all_documents(reprocess_existing=args.reprocess_existing)

        if not documents:
            if summary["skipped_existing"] > 0 and summary["failed_files"] == 0:
                print("✅ No new documents required indexing. Existing Qdrant data is being reused.")
                return
            print("❌ No documents to process. Make sure you have documents in the 'data/' folder.")
            print("💡 Supported formats: PDF, CSV, JSON, TXT, MD")
            return

        # Add documents to vector store using batch processing
        print(f"\n🗄️ Adding {len(documents)} document chunks to Qdrant...")
        add_documents_batch(documents, batch_size=100)

        print(f"\n🎉 Document processing completed successfully!")
        print(
            f"📌 Run summary: processed={summary['processed_files']}, "
            f"skipped_existing={summary['skipped_existing']}, failed={summary['failed_files']}, "
            f"new_chunks={summary['total_chunks']}"
        )
        print(f"📊 Collection '{QDRANT_COLLECTION_NAME}' is ready for the chat application")
        print("🚀 You can now run the chat application:")
        print("   - Backend: cd backend && uvicorn main:app --reload")
        print("   - Frontend: cd frontend && streamlit run app.py")
        print("\n💡 Make sure to set your API keys in the .env file:")
        print("   - QDRANT_API_KEY and QDRANT_URL")
        print("   - GOOGLE_API_KEY")
        print("   - TAVILY_API_KEY")

    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your .env file has the required API keys")
        print("   2. Ensure Qdrant cloud instance is accessible")
        print("   3. Verify documents are in the 'data/' folder")


if __name__ == "__main__":
    main()
