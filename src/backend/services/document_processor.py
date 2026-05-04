"""
Document Processing Service for FSS Hero Chatbot
Unified document processing logic for both bulk and API uploads.
Handles PDF, CSV, JSON, TXT, and MD files with consistent chunking and metadata.
"""

import os
import io
import json
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import UploadFile
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.backend.core.config import (
    DOC_CHUNK_SIZE,
    DOC_CHUNK_OVERLAP,
    DOC_SUPPORTED_FORMATS,
    DOC_MAX_UPLOAD_SIZE
)


class DocumentProcessingError(Exception):
    """Custom exception for document processing errors"""
    pass


class DocumentProcessor:
    """
    Unified document processor for FSS Hero Chatbot.
    Handles all document types with consistent chunking and metadata.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        supported_formats: List[str] = None
    ):
        """
        Initialize DocumentProcessor.

        Args:
            chunk_size: Size of text chunks (default from config)
            chunk_overlap: Overlap between chunks (default from config)
            supported_formats: List of supported file formats (default from config)
        """
        self.chunk_size = chunk_size or DOC_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or DOC_CHUNK_OVERLAP
        self.supported_formats = supported_formats or DOC_SUPPORTED_FORMATS
        self.max_upload_size = DOC_MAX_UPLOAD_SIZE

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

    def process_file(self, file_path: str, source: str = "bulk") -> List[Document]:
        """
        Process a file from the file system.

        Args:
            file_path: Path to the file to process
            source: Source of the file ("bulk" or "api")

        Returns:
            List of Document objects with content and metadata

        Raises:
            DocumentProcessingError: If processing fails
        """
        if not os.path.exists(file_path):
            raise DocumentProcessingError(f"File not found: {file_path}")

        if not self._validate_file(file_path):
            raise DocumentProcessingError(f"Unsupported file format: {file_path}")

        file_ext = Path(file_path).suffix.lower().lstrip('.')
        file_name = os.path.basename(file_path)
        derived_metadata = self._derive_metadata_from_path(file_path)

        # Base metadata
        base_metadata = {
            "file_name": file_name,
            "source_type": file_ext,
            "upload_source": source,
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
        }
        base_metadata.update(derived_metadata)

        try:
            # Process based on file type
            if file_ext == 'pdf':
                documents = self._process_pdf(file_path, base_metadata)
            elif file_ext == 'csv':
                documents = self._process_csv(file_path, base_metadata)
            elif file_ext == 'json':
                documents = self._process_json(file_path, base_metadata)
            elif file_ext in ['txt', 'md']:
                documents = self._process_text(file_path, base_metadata)
            else:
                raise DocumentProcessingError(f"Unsupported file type: {file_ext}")

            # Chunk documents
            chunked_documents = self._chunk_documents(documents)

            # Add chunk metadata
            chunked_documents = self._add_metadata(chunked_documents, base_metadata)

            return chunked_documents

        except Exception as e:
            raise DocumentProcessingError(f"Error processing {file_name}: {str(e)}")

    async def process_upload(
        self,
        file: UploadFile,
        metadata: Dict[str, Any] = None
    ) -> List[Document]:
        """
        Process an uploaded file from API.

        Args:
            file: FastAPI UploadFile object
            metadata: Optional additional metadata to add

        Returns:
            List of Document objects with content and metadata

        Raises:
            DocumentProcessingError: If processing fails
        """
        # Validate file format
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        if file_ext not in self.supported_formats:
            raise DocumentProcessingError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )

        # Read file content and check size
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > self.max_upload_size:
            max_mb = self.max_upload_size / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            raise DocumentProcessingError(
                f"File too large: {actual_mb:.2f}MB. Maximum size: {max_mb:.2f}MB"
            )

        if file_size == 0:
            raise DocumentProcessingError("File is empty")

        # Base metadata
        base_metadata = {
            "file_name": file.filename,
            "source_type": file_ext,
            "upload_source": "api",
            "timestamp": datetime.now().isoformat(),
            "file_size": file_size
        }

        # Add any additional metadata
        if metadata:
            base_metadata.update(metadata)

        # Create temporary file for processing
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name

            # Process the temporary file
            documents = []

            if file_ext == 'pdf':
                documents = self._process_pdf(tmp_file_path, base_metadata)
            elif file_ext == 'csv':
                documents = self._process_csv(tmp_file_path, base_metadata)
            elif file_ext == 'json':
                documents = self._process_json(tmp_file_path, base_metadata)
            elif file_ext in ['txt', 'md']:
                documents = self._process_text(tmp_file_path, base_metadata)

            # Chunk documents
            chunked_documents = self._chunk_documents(documents)

            # Add chunk metadata
            chunked_documents = self._add_metadata(chunked_documents, base_metadata)

            return chunked_documents

        except Exception as e:
            raise DocumentProcessingError(f"Error processing upload {file.filename}: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    def _process_pdf(self, file_path: str, metadata: Dict[str, Any]) -> List[Document]:
        """
        Process PDF file.

        Args:
            file_path: Path to PDF file
            metadata: Base metadata to add

        Returns:
            List of Document objects
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()

            # Add metadata to each document
            for doc in documents:
                doc.metadata.update(metadata)

            return documents

        except Exception as e:
            raise DocumentProcessingError(f"PDF processing error: {str(e)}")

    def _process_csv(self, file_path: str, metadata: Dict[str, Any]) -> List[Document]:
        """
        Process CSV file.

        Args:
            file_path: Path to CSV file
            metadata: Base metadata to add

        Returns:
            List of Document objects
        """
        try:
            loader = CSVLoader(file_path=file_path)
            documents = loader.load()

            # Add metadata to each document
            for doc in documents:
                doc.metadata.update(metadata)

            return documents

        except Exception as e:
            raise DocumentProcessingError(f"CSV processing error: {str(e)}")

    def _process_json(self, file_path: str, metadata: Dict[str, Any]) -> List[Document]:
        """
        Process JSON file.

        Args:
            file_path: Path to JSON file
            metadata: Base metadata to add

        Returns:
            List of Document objects
        """
        try:
            loader = JSONLoader(
                file_path=file_path,
                jq_schema='.',
                text_content=False
            )
            documents = loader.load()

            # Add metadata to each document
            for doc in documents:
                doc.metadata.update(metadata)

            return documents

        except Exception as e:
            raise DocumentProcessingError(f"JSON processing error: {str(e)}")

    def _process_text(self, file_path: str, metadata: Dict[str, Any]) -> List[Document]:
        """
        Process plain text file (TXT or MD).

        Args:
            file_path: Path to text file
            metadata: Base metadata to add

        Returns:
            List of Document objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                raise DocumentProcessingError("Text file is empty")

            # Create document
            doc = Document(
                page_content=content,
                metadata=metadata.copy()
            )

            return [doc]

        except Exception as e:
            raise DocumentProcessingError(f"Text processing error: {str(e)}")

    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Chunk documents into smaller pieces.

        Args:
            documents: List of documents to chunk

        Returns:
            List of chunked documents
        """
        if not documents:
            return []

        try:
            chunked_documents = self.text_splitter.split_documents(documents)
            return chunked_documents
        except Exception as e:
            raise DocumentProcessingError(f"Chunking error: {str(e)}")

    def _add_metadata(
        self,
        documents: List[Document],
        base_metadata: Dict[str, Any]
    ) -> List[Document]:
        """
        Add standardized metadata to all document chunks.

        Args:
            documents: List of documents to add metadata to
            base_metadata: Base metadata to add

        Returns:
            List of documents with enhanced metadata
        """
        total_chunks = len(documents)

        for idx, doc in enumerate(documents):
            # Ensure base metadata is present
            doc.metadata.update(base_metadata)

            # Add chunk-specific metadata
            doc.metadata.update({
                "chunk_index": idx,
                "total_chunks": total_chunks
            })

        return documents

    def _validate_file(self, file_path: str) -> bool:
        """
        Validate file format.

        Args:
            file_path: Path to file

        Returns:
            True if file format is supported, False otherwise
        """
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        return file_ext in self.supported_formats

    def _derive_metadata_from_path(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        normalized = path.as_posix().lower()
        stem = path.stem

        category = "general"
        if "staff_details" in normalized or "lecturer" in normalized:
            category = "faculty"
        elif "support_staff" in normalized or "officials" in normalized:
            category = "staff"
        elif "program" in normalized or "หลักสูตร" in normalized:
            category = "academic"
        elif "contact" in normalized:
            category = "contact"
        elif "regulation" in normalized or "ระเบียบ" in normalized:
            category = "policy"

        title = stem.replace("_", " ").strip()
        return {
            "document_category": category,
            "title": title,
        }


# Global instance for use across the application
document_processor = DocumentProcessor()
