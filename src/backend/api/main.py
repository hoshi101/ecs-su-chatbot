import os
import time
from typing import List, Dict, Any, Optional
import uuid
import traceback

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Query, Request
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.backend.core.agent import (
    build_chat_model,
    enhance_query_hero_bot_style,
    get_available_model_suggestions,
    get_default_llm_settings,
    rag_agent,
)
from src.backend.services.vectorstore import (
    add_documents_batch,
    get_documents_by_metadata,
    delete_documents_by_metadata,
    get_collection_stats,
    embeddings,
    _get_qdrant_client
)
from src.backend.services.document_processor import document_processor, DocumentProcessingError
from src.backend.core.config import (
    GEMINI_MODEL,
    QDRANT_COLLECTION_NAME,
    ENABLE_QUERY_ENHANCEMENT,
    OPENAI_API_KEY,
    TAVILY_API_KEY,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_PER_MINUTE,
    BOT_NAME,
    DOMAIN_NAME,
    SEARCH_DOMAINS,
    normalize_provider,
    resolve_model_name,
)
from langchain_qdrant import QdrantVectorStore
from src.backend.utils.logging_utils import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EE Support Assistant API",
    description="API for the Electrical Engineering Department support chatbot powered by Qdrant, configurable LLM providers, and BGE-M3.",
    version="2.0.0",
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In-memory session manager for LangGraph checkpoints (for demonstration)
memory = MemorySaver()

# --- Pydantic Models for API ---
class TraceEvent(BaseModel):
    step: int
    node_name: str
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)
    event_type: str

class QueryRequest(BaseModel):
    session_id: str
    query: str
    enable_web_search: bool = True # NEW: Add web search toggle state
    force_web_search: bool = False # NEW: Force web search override
    similarity_threshold: float = 0.7 # NEW: Search relevance threshold (0.0-1.0)
    llm_provider: str | None = Field(None, description="LLM provider to use: gemini or openai")
    llm_model: str | None = Field(None, description="Exact model name for the selected provider")

class AgentResponse(BaseModel):
    response: str
    trace_events: List[TraceEvent] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    llm_provider: str | None = None
    llm_model: str | None = None


class LLMOptionsResponse(BaseModel):
    default_provider: str
    default_model: str
    providers: Dict[str, List[str]]


def _safe_snippet(content: str, limit: int = 320) -> str:
    text = (content or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _load_sidecar_source_metadata(file_path: str | None) -> Dict[str, Any]:
    if not file_path:
        return {}

    sidecar_path = os.path.splitext(file_path)[0] + ".json"
    if not os.path.exists(sidecar_path):
        return {}

    try:
        import json

        with open(sidecar_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return {}

    return {
        "source_url": payload.get("source_url"),
        "title": payload.get("title"),
        "document_category": payload.get("category"),
    }


def _build_rag_source_reference(doc: Dict[str, Any]) -> Dict[str, Any]:
    metadata = doc.get("metadata", {})
    sidecar_metadata = _load_sidecar_source_metadata(metadata.get("file_path"))
    merged_metadata = {**sidecar_metadata, **metadata}
    title = merged_metadata.get("title") or merged_metadata.get("file_name") or "Knowledge Base Document"
    content = doc.get("content", "")

    if str(title).lower().startswith("lecturer "):
        first_line = content.splitlines()[0].strip("# ").strip()
        if first_line:
            title = first_line

    return {
        "title": title,
        "snippet": _safe_snippet(content),
        "relevance_score": doc.get("score"),
        "source_type": "Department Knowledge Base",
        "file_name": merged_metadata.get("file_name"),
        "file_path": merged_metadata.get("file_path"),
        "source_url": merged_metadata.get("source_url"),
        "document_category": merged_metadata.get("document_category"),
        "page": merged_metadata.get("page"),
        "page_label": merged_metadata.get("page_label"),
        "chunk_index": merged_metadata.get("chunk_index"),
        "total_chunks": merged_metadata.get("total_chunks"),
        "content_hash": merged_metadata.get("content_hash"),
    }


def _build_web_source_reference(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": result.get("title") or "Official Website Result",
        "snippet": _safe_snippet(result.get("snippet", "")),
        "relevance_score": result.get("relevance"),
        "source_type": "Official Website Search",
        "source_url": result.get("url"),
    }

class DocumentUploadResponse(BaseModel):
    message: str
    filename: str
    processed_chunks: int
    document_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentInfo(BaseModel):
    id: str
    metadata: Dict[str, Any]
    content_preview: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total: int
    page: int
    page_size: int

class DocumentDeleteResponse(BaseModel):
    message: str
    deleted_count: int

class CollectionStatsResponse(BaseModel):
    total_documents: int
    by_source_type: Dict[str, int]
    by_upload_source: Dict[str, int]
    collection_name: str

# --- Testing and Monitoring Pydantic Models ---

class RetrievalTestRequest(BaseModel):
    query: str = Field(..., description="Query to test retrieval with")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold for retrieval (0.0-1.0)")
    top_k: int = Field(5, ge=1, le=20, description="Number of top results to retrieve")
    return_scores: bool = Field(True, description="Include similarity scores in response")
    return_metadata: bool = Field(True, description="Include document metadata in response")

class RetrievalResult(BaseModel):
    content: str = Field(..., description="Retrieved document content")
    score: Optional[float] = Field(None, description="Similarity score (if return_scores=True)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata (if return_metadata=True)")
    chunk_info: Optional[Dict[str, Any]] = Field(None, description="Chunk-specific information")

class RetrievalTestResponse(BaseModel):
    original_query: str
    enhanced_query: Optional[str] = None
    query_enhancement_enabled: bool
    results: List[RetrievalResult]
    total_results: int
    retrieval_latency_ms: float
    collection_stats: Dict[str, Any]
    search_parameters: Dict[str, Any]

class ComponentHealth(BaseModel):
    name: str
    status: str = Field(..., description="healthy, degraded, or unhealthy")
    latency_ms: Optional[float] = None
    details: Optional[str] = None
    error: Optional[str] = None

class SystemHealthResponse(BaseModel):
    overall_status: str = Field(..., description="healthy, degraded, or unhealthy")
    timestamp: str
    components: List[ComponentHealth]
    summary: Dict[str, Any]

class EmbeddingTestRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=10, description="List of texts to embed (max 10)")
    reference_text: Optional[str] = Field(None, description="Optional reference text to compare against")
    compute_similarities: bool = Field(False, description="Compute cosine similarities between all texts")

class EmbeddingResult(BaseModel):
    text: str
    text_preview: str = Field(..., description="First 100 characters of text")
    embedding_dimensions: int
    similarity_to_reference: Optional[float] = None

class EmbeddingTestResponse(BaseModel):
    results: List[EmbeddingResult]
    total_texts: int
    processing_time_ms: float
    embedding_model: str
    similarity_matrix: Optional[List[List[float]]] = Field(None, description="Pairwise similarity matrix (if compute_similarities=True)")


# --- Document Upload Endpoints ---
# async def _upload_document_logic(file: UploadFile) -> DocumentUploadResponse:
#     """
#     Shared logic for document upload endpoints.
#
#     Uploads a document (PDF, CSV, JSON, TXT, MD), processes it with chunking,
#     and adds it to the RAG knowledge base with proper metadata.
#
#     CRITICAL FIX: Documents are now chunked (previously they were stored as single large text).
#     This significantly improves retrieval accuracy.
#     """
#     print(f"📥 Received file for upload: {file.filename}")
#
#     try:
#         # Generate unique document ID
#         document_id = str(uuid.uuid4())
#
#         # Additional metadata for API uploads
#         additional_metadata = {
#             "document_id": document_id,
#             "upload_method": "api"
#         }
#
#         # Process the uploaded file using DocumentProcessor
#         # This will:
#         # 1. Validate file format and size
#         # 2. Extract content based on file type
#         # 3. Chunk the content (CRITICAL: this was missing before!)
#         # 4. Add standardized metadata to all chunks
#         documents = await document_processor.process_upload(file, additional_metadata)
#
#         if not documents:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="No content could be extracted from the file."
#             )
#
#         # Add documents to vector store in batch
#         add_documents_batch(documents, batch_size=100)
#
#         # Extract metadata from first chunk for response
#         response_metadata = {
#             "file_name": documents[0].metadata.get("file_name"),
#             "source_type": documents[0].metadata.get("source_type"),
#             "upload_source": documents[0].metadata.get("upload_source"),
#             "timestamp": documents[0].metadata.get("timestamp"),
#             "total_chunks": len(documents)
#         }
#
#         print(f"✅ Successfully processed {file.filename}: {len(documents)} chunks created")
#
#         return DocumentUploadResponse(
#             message=f"Document '{file.filename}' successfully uploaded and indexed with {len(documents)} chunks.",
#             filename=file.filename,
#             processed_chunks=len(documents),
#             document_id=document_id,
#             metadata=response_metadata
#         )
#
#     except DocumentProcessingError as e:
#         print(f"❌ Document processing error: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#     except Exception as e:
#         print(f"❌ Unexpected error processing document: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to process document: {str(e)}"
#         )


# @app.post("/documents/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_200_OK)
# async def upload_document_new(file: UploadFile = File(...)):
#     """
#     Primary document upload endpoint (RESTful naming convention).
#
#     Uploads a document (PDF, CSV, JSON, TXT, MD), processes it with chunking,
#     and adds it to the RAG knowledge base with proper metadata.
#
#     Supported formats: PDF, CSV, JSON, TXT, MD
#     Maximum file size: 50MB (configurable)
#     """
#     return await _upload_document_logic(file)
#
#
# @app.post("/upload-document/", response_model=DocumentUploadResponse, status_code=status.HTTP_200_OK, deprecated=True)
# async def upload_document_legacy(file: UploadFile = File(...)):
#     """
#     DEPRECATED: Use /documents/upload instead.
#
#     Legacy document upload endpoint maintained for backwards compatibility.
#     Will be removed in a future version.
#     """
#     return await _upload_document_logic(file)


# --- Document Management Endpoints ---
#
# @app.get("/documents/stats", response_model=CollectionStatsResponse)
# async def get_stats():
#     """
#     Get statistics about the document collection.
#
#     Returns:
#     - Total document count
#     - Count by source type (pdf, csv, json, txt, md)
#     - Count by upload source (bulk, api)
#     - Collection name
#     """
#     try:
#         stats = get_collection_stats()
#         return CollectionStatsResponse(**stats)
#
#     except Exception as e:
#         print(f"❌ Error getting collection stats: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to get collection stats: {str(e)}"
#         )


# @app.get("/documents/", response_model=DocumentListResponse)
# async def list_documents(
#     page: int = Query(1, ge=1, description="Page number (starting from 1)"),
#     page_size: int = Query(20, ge=1, le=100, description="Number of documents per page"),
#     source_type: Optional[str] = Query(None, description="Filter by source type (pdf, csv, json, txt, md)"),
#     upload_source: Optional[str] = Query(None, description="Filter by upload source (bulk, api)")
# ):
#     """
#     List documents with optional filtering and pagination.
#
#     Query Parameters:
#     - page: Page number (default: 1)
#     - page_size: Items per page (default: 20, max: 100)
#     - source_type: Filter by document type (pdf, csv, json, txt, md)
#     - upload_source: Filter by upload method (bulk, api)
#     """
#     try:
#         # Build filters
#         filters = {}
#         if source_type:
#             filters["source_type"] = source_type
#         if upload_source:
#             filters["upload_source"] = upload_source
#
#         # Get documents from vector store
#         all_documents = get_documents_by_metadata(filters) if filters else get_documents_by_metadata({})
#
#         # Apply pagination
#         total = len(all_documents)
#         start_idx = (page - 1) * page_size
#         end_idx = start_idx + page_size
#         paginated_docs = all_documents[start_idx:end_idx]
#
#         # Convert to response format
#         document_infos = [
#             DocumentInfo(
#                 id=str(doc["id"]),
#                 metadata=doc["metadata"],
#                 content_preview=doc["content_preview"]
#             )
#             for doc in paginated_docs
#         ]
#
#         return DocumentListResponse(
#             documents=document_infos,
#             total=total,
#             page=page,
#             page_size=page_size
#         )
#
#     except Exception as e:
#         print(f"❌ Error listing documents: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to list documents: {str(e)}"
#         )


# @app.get("/documents/{document_id}", response_model=DocumentInfo)
# async def get_document(document_id: str):
#     """
#     Get a specific document by ID.
#
#     Path Parameters:
#     - document_id: UUID of the document to retrieve
#     """
#     try:
#         # Query by document_id
#         documents = get_documents_by_metadata({"document_id": document_id})
#
#         if not documents:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Document with ID '{document_id}' not found"
#             )
#
#         # Return first matching document (should be unique by document_id)
#         doc = documents[0]
#         return DocumentInfo(
#             id=str(doc["id"]),
#             metadata=doc["metadata"],
#             content_preview=doc["content_preview"]
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Error getting document: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to get document: {str(e)}"
#         )


# @app.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
# async def delete_document(document_id: str):
#     """
#     Delete a document and all its chunks by document ID.
#
#     Path Parameters:
#     - document_id: UUID of the document to delete
#
#     Returns:
#     - Number of chunks deleted
#     """
#     try:
#         # Delete all chunks with this document_id
#         deleted_count = delete_documents_by_metadata({"document_id": document_id})
#
#         if deleted_count == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Document with ID '{document_id}' not found"
#             )
#
#         return DocumentDeleteResponse(
#             message=f"Successfully deleted document '{document_id}' ({deleted_count} chunks removed)",
#             deleted_count=deleted_count
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Error deleting document: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to delete document: {str(e)}"
#         )


# --- Chat Endpoint ---
@app.post("/chat/", response_model=AgentResponse)
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute" if RATE_LIMIT_ENABLED else "1000000/minute")
async def chat_with_agent(request: Request, body: QueryRequest):
    trace_events_for_frontend: List[TraceEvent] = []

    try:
        llm_provider = normalize_provider(body.llm_provider)
        llm_model = resolve_model_name(llm_provider, body.llm_model)

        # Pass enhanced parameters into the config for the agent to access
        config = {
            "configurable": {
                "thread_id": body.session_id
            }
        }
        inputs = {
            "messages": [HumanMessage(content=body.query)],
            "web_search_enabled": body.enable_web_search,
            "force_web_search": body.force_web_search,
            "similarity_threshold": body.similarity_threshold,
            "llm_provider": llm_provider,
            "llm_model": llm_model,
        }

        final_message = ""

        logger.info(
            "Starting agent stream | session_id=%s | provider=%s | model=%s | web_search=%s | force_web_search=%s | similarity_threshold=%s",
            body.session_id,
            llm_provider,
            llm_model,
            body.enable_web_search,
            body.force_web_search,
            body.similarity_threshold,
        )

        for i, s in enumerate(rag_agent.stream(inputs, config=config)):
            current_node_name = None
            node_output_state = None

            if '__end__' in s:
                current_node_name = '__end__'
                node_output_state = s['__end__']
            else:
                current_node_name = list(s.keys())[0]
                node_output_state = s[current_node_name]

            event_description = f"Executing node: {current_node_name}"
            event_details = {}
            event_type = "generic_node_execution"

            if current_node_name == "router":
                route_decision = node_output_state.get('route')
                initial_decision = node_output_state.get('initial_router_decision', route_decision)
                override_reason = node_output_state.get('router_override_reason', None)
                original_query = node_output_state.get('original_query', body.query)
                enhanced_query = node_output_state.get('enhanced_query', body.query)
                enhancement_status = node_output_state.get("query_enhancement_status", "unchanged")
                enhancement_reason = node_output_state.get("query_enhancement_reason", "")
                precheck_intent = node_output_state.get("precheck_intent")
                precheck_reason = node_output_state.get("precheck_reason", "")
                precheck_variant = node_output_state.get("precheck_variant", "")
                precheck_source = node_output_state.get("precheck_source", "")
                query_enhanced = enhanced_query != original_query and node_output_state.get('query_enhancement_enabled', False)

                if route_decision == "end" and precheck_intent in {"contact", "greeting", "out_of_scope"}:
                    event_description = f"Shortcut response selected for '{precheck_intent}'."
                    event_details = {
                        "decision": route_decision,
                        "shortcut_type": precheck_intent,
                        "shortcut_variant": precheck_variant,
                        "shortcut_source": precheck_source,
                        "precheck_intent": precheck_intent,
                        "precheck_reason": precheck_reason,
                        "original_query": original_query,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                    }
                elif query_enhanced:
                    event_description = f"Query was refined for retrieval and routed to '{route_decision}'."
                    event_details = {
                        "decision": route_decision,
                        "original_query": original_query,
                        "enhanced_query": enhanced_query,
                        "query_enhanced": True,
                        "query_enhancement_status": enhancement_status,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                        "reason": enhancement_reason or "Query was clarified for department knowledge base search"
                    }
                elif override_reason:
                    event_description = f"Router initially decided: '{initial_decision}'. Overridden to: '{route_decision}' because {override_reason}."
                    event_details = {
                        "initial_decision": initial_decision,
                        "final_decision": route_decision,
                        "override_reason": override_reason,
                        "original_query": original_query,
                        "enhanced_query": enhanced_query,
                        "query_enhanced": query_enhanced,
                        "query_enhancement_status": enhancement_status,
                        "query_enhancement_reason": enhancement_reason,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                    }
                elif enhancement_status == "skipped":
                    event_description = f"Router skipped query enhancement and decided to use '{route_decision}'."
                    event_details = {
                        "decision": route_decision,
                        "reason": "Based on department information routing policy",
                        "original_query": original_query,
                        "enhanced_query": enhanced_query,
                        "query_enhanced": False,
                        "query_enhancement_status": enhancement_status,
                        "query_enhancement_reason": enhancement_reason,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                    }
                else:
                    event_description = f"Router decided to use '{route_decision}'."
                    event_details = {
                        "decision": route_decision,
                        "reason": "Based on department information routing policy",
                        "original_query": original_query,
                        "enhanced_query": enhanced_query,
                        "query_enhanced": query_enhanced,
                        "query_enhancement_status": enhancement_status,
                        "query_enhancement_reason": enhancement_reason,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                    }
                event_type = "routing"
            elif current_node_name == "rag_lookup":
                rag_content_summary = node_output_state.get("rag", "")[:200] + "..."
                rag_status = node_output_state.get("rag_status")
                enhanced_query = node_output_state.get("enhanced_query", "")
                retrieved_docs = [
                    _build_rag_source_reference(doc)
                    for doc in node_output_state.get("rag_documents", [])
                ]

                if rag_status == "sufficient":
                    event_description = "Found sufficient department knowledge base content."
                    event_details = {
                        "retrieved_content_summary": rag_content_summary,
                        "sufficiency_verdict": "Sufficient for department question",
                        "enhanced_query": enhanced_query,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                        "search_type": "Department Knowledge Base Search",
                        "retrieved_documents": retrieved_docs
                    }
                elif rag_status == "error":
                    event_description = "Knowledge base retrieval failed. Continuing without RAG evidence."
                    event_details = {
                        "retrieved_content_summary": rag_content_summary,
                        "sufficiency_verdict": "Retrieval error",
                        "enhanced_query": enhanced_query,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                        "search_type": "Department Knowledge Base Search",
                        "retrieved_documents": retrieved_docs,
                        "error": node_output_state.get("rag_error"),
                    }
                elif rag_status == "empty":
                    event_description = "Knowledge base search returned no matching content."
                    event_details = {
                        "retrieved_content_summary": rag_content_summary,
                        "sufficiency_verdict": "No matching knowledge base content",
                        "enhanced_query": enhanced_query,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                        "search_type": "Department Knowledge Base Search",
                        "retrieved_documents": retrieved_docs
                    }
                else:
                    event_description = "Knowledge base content was incomplete. Proceeding to official website search."
                    event_details = {
                        "retrieved_content_summary": rag_content_summary,
                        "sufficiency_verdict": "Not sufficient - trying official website search",
                        "enhanced_query": enhanced_query,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                        "search_type": "Department Knowledge Base Search",
                        "retrieved_documents": retrieved_docs
                    }

                event_type = "rag_search"
            elif current_node_name == "web_search":
                web_content_summary = node_output_state.get("web", "")[:200] + "..."
                enhanced_query = node_output_state.get("enhanced_query", "")
                web_results = node_output_state.get("web_results", [])

                if not web_results and not web_content_summary.strip():
                    event_description = "Official website search was unavailable or returned no usable result."
                    event_details = {
                        "search_status": "empty",
                        "enhanced_query": enhanced_query,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                        "message": "No additional official website result was available"
                    }
                else:
                    event_description = "Searched official department/faculty websites for supporting information."
                    event_details = {
                        "retrieved_content_summary": web_content_summary,
                        "enhanced_query": enhanced_query,
                        "llm_provider": node_output_state.get("llm_provider"),
                        "llm_model": node_output_state.get("llm_model"),
                        "search_domains": ", ".join(SEARCH_DOMAINS),
                        "search_type": "Official Website Search",
                        "search_results": [
                            _build_web_source_reference(result)
                            for result in web_results
                        ]
                    }
                event_type = "web_search"
            elif current_node_name == "answer":
                enhanced_query = node_output_state.get("enhanced_query", "")
                event_description = "Generating the final department support response."
                event_details = {
                    "bot_name": BOT_NAME,
                    "specialization": DOMAIN_NAME,
                    "enhanced_query": enhanced_query,
                    "llm_provider": node_output_state.get("llm_provider"),
                    "llm_model": node_output_state.get("llm_model"),
                    "response_type": "Department Information Response"
                }
                event_type = "response_generation"
            elif current_node_name == "__end__":
                event_description = "Agent process completed."
                event_type = "process_end"

            trace_events_for_frontend.append(
                TraceEvent(
                    step=i + 1,
                    node_name=current_node_name,
                    description=event_description,
                    details=event_details,
                    event_type=event_type
                )
            )
            logger.info(
                "Streamed event | session_id=%s | step=%s | node=%s | description=%s",
                body.session_id,
                i + 1,
                current_node_name,
                event_description,
            )

        # Get the final state from the last yielded item in the stream
        final_actual_state_dict = None
        if s:
            if '__end__' in s:
                final_actual_state_dict = s['__end__']
            else:
                if list(s.keys()):
                    final_actual_state_dict = s[list(s.keys())[0]]

        if final_actual_state_dict and "messages" in final_actual_state_dict:
            for msg in reversed(final_actual_state_dict["messages"]):
                if isinstance(msg, AIMessage):
                    final_message = msg.content
                    break

        if not final_message:
             logger.error("Agent finished without final AIMessage | session_id=%s", body.session_id)
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Agent did not return a valid response (final AI message not found).")

        final_sources: List[Dict[str, Any]] = []
        if final_actual_state_dict:
            final_sources.extend(
                _build_rag_source_reference(doc)
                for doc in final_actual_state_dict.get("rag_documents", [])
            )
            final_sources.extend(
                _build_web_source_reference(result)
                for result in final_actual_state_dict.get("web_results", [])
            )

        logger.info(
            "Agent stream completed | session_id=%s | response_preview=%s | sources=%s",
            body.session_id,
            final_message[:200],
            len(final_sources),
        )

        return AgentResponse(
            response=final_message,
            trace_events=trace_events_for_frontend,
            sources=final_sources,
            llm_provider=final_actual_state_dict.get("llm_provider") if final_actual_state_dict else llm_provider,
            llm_model=final_actual_state_dict.get("llm_model") if final_actual_state_dict else llm_model,
        )

    except Exception as e:
        traceback.print_exc()
        error_details = f"Error during agent invocation: {e}"
        logger.exception("%s | session_id=%s", error_details, body.session_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/llm/options", response_model=LLMOptionsResponse)
async def llm_options():
    defaults = get_default_llm_settings()
    return LLMOptionsResponse(
        default_provider=defaults["provider"],
        default_model=defaults["model"],
        providers=get_available_model_suggestions(),
    )


# --- Testing and Monitoring Endpoints ---

@app.post("/debug/retrieval-test", response_model=RetrievalTestResponse)
async def test_retrieval(request: RetrievalTestRequest):
    """
    Test and debug RAG retrieval with detailed results.

    This endpoint is essential for:
    - Testing retrieval quality and relevance
    - Debugging similarity thresholds
    - Understanding what documents are being retrieved
    - Analyzing query enhancement effectiveness

    Use Cases:
    - Verify new documents are indexed correctly
    - Test different similarity thresholds
    - Debug retrieval issues in production
    - Compare original vs enhanced queries

    Example:
        POST /debug/retrieval-test
        {
            "query": "How to set stop loss?",
            "similarity_threshold": 0.7,
            "top_k": 5,
            "return_scores": true,
            "return_metadata": true
        }
    """
    logger.info(
        "Retrieval test started | query=%s | threshold=%s | top_k=%s",
        request.query,
        request.similarity_threshold,
        request.top_k,
    )

    try:
        start_time = time.time()

        # Step 1: Test query enhancement if enabled
        original_query = request.query
        enhanced_query = None

        if ENABLE_QUERY_ENHANCEMENT:
            try:
                enhanced_query = enhance_query_hero_bot_style(original_query)
                logger.info("Query enhanced | original=%s | enhanced=%s", original_query, enhanced_query)
            except Exception as e:
                logger.warning("Query enhancement failed | error=%s", e)
                enhanced_query = original_query
        else:
            enhanced_query = original_query
            logger.info("Query enhancement disabled")

        # Use enhanced query for retrieval
        query_to_use = enhanced_query if enhanced_query else original_query

        # Step 2: Perform similarity search using Qdrant
        try:
            client = _get_qdrant_client()
            vectorstore = QdrantVectorStore(
                client=client,
                collection_name=QDRANT_COLLECTION_NAME,
                embedding=embeddings
            )

            # Configure retriever based on similarity threshold
            if request.similarity_threshold < 1.0:
                retriever = vectorstore.as_retriever(
                    search_type="similarity_score_threshold",
                    search_kwargs={
                        "k": request.top_k,
                        "score_threshold": request.similarity_threshold
                    }
                )
            else:
                retriever = vectorstore.as_retriever(
                    search_kwargs={"k": request.top_k}
                )

            # Retrieve documents
            retrieval_start = time.time()

            # Use similarity_search_with_score for detailed results
            if request.return_scores:
                search_results = vectorstore.similarity_search_with_score(
                    query_to_use,
                    k=request.top_k
                )
                documents = [(doc, score) for doc, score in search_results]
            else:
                docs = retriever.invoke(query_to_use)
                documents = [(doc, None) for doc in docs]

            retrieval_latency = (time.time() - retrieval_start) * 1000

            logger.info("Retrieval test completed | results=%s | latency_ms=%.2f", len(documents), retrieval_latency)

        except Exception as e:
            logger.exception("Retrieval error | query=%s", query_to_use)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Retrieval failed: {str(e)}"
            )

        # Step 3: Build detailed results
        results = []
        for doc, score in documents:
            result = RetrievalResult(
                content=doc.page_content,
                score=float(score) if score is not None and request.return_scores else None,
                metadata=doc.metadata if request.return_metadata else None,
                chunk_info={
                    "chunk_index": doc.metadata.get("chunk_index"),
                    "total_chunks": doc.metadata.get("total_chunks"),
                    "file_name": doc.metadata.get("file_name"),
                    "source_type": doc.metadata.get("source_type")
                } if request.return_metadata else None
            )
            results.append(result)

        # Step 4: Get collection statistics for context
        try:
            collection_stats = get_collection_stats()
        except Exception as e:
            logger.warning("Could not get collection stats | error=%s", e)
            collection_stats = {"error": str(e)}

        total_time = (time.time() - start_time) * 1000

        logger.info("Retrieval test request finished | total_time_ms=%.2f", total_time)

        return RetrievalTestResponse(
            original_query=original_query,
            enhanced_query=enhanced_query if enhanced_query != original_query else None,
            query_enhancement_enabled=ENABLE_QUERY_ENHANCEMENT,
            results=results,
            total_results=len(results),
            retrieval_latency_ms=retrieval_latency,
            collection_stats=collection_stats,
            search_parameters={
                "similarity_threshold": request.similarity_threshold,
                "top_k": request.top_k,
                "return_scores": request.return_scores,
                "return_metadata": request.return_metadata
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        logger.exception("Retrieval test failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval test failed: {str(e)}"
        )


@app.get("/health/detailed", response_model=SystemHealthResponse)
async def detailed_health_check():
    """
    Comprehensive health check for all system components.

    This endpoint checks:
    - Qdrant connection and collection status
    - BGE-M3 embedding generation
    - Configured LLM provider connectivity (Gemini and/or OpenAI)
    - Tavily web search (if configured)
    - DocumentProcessor initialization

    Returns overall system health status and individual component details.

    Status Levels:
    - healthy: All components operational
    - degraded: Some non-critical components failing
    - unhealthy: Critical components failing

    Use Cases:
    - Monitoring system health in production
    - Debugging connectivity issues
    - Validating configuration changes
    - Pre-deployment health verification

    Example:
        GET /health/detailed
    """
    logger.info("Detailed health check started")

    from datetime import datetime
    timestamp = datetime.now().isoformat()
    components: List[ComponentHealth] = []

    # Track critical component failures
    critical_failures = 0
    non_critical_failures = 0

    # 1. Check Qdrant connection and collection
    logger.info("Checking Qdrant")
    try:
        start = time.time()
        client = _get_qdrant_client()

        # Verify collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if QDRANT_COLLECTION_NAME in collection_names:
            collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
            latency = (time.time() - start) * 1000

            components.append(ComponentHealth(
                name="Qdrant Vector Database",
                status="healthy",
                latency_ms=round(latency, 2),
                details=f"Collection '{QDRANT_COLLECTION_NAME}' found with {collection_info.points_count} documents"
            ))
            logger.info("Qdrant healthy | latency_ms=%.2f", latency)
        else:
            latency = (time.time() - start) * 1000
            components.append(ComponentHealth(
                name="Qdrant Vector Database",
                status="degraded",
                latency_ms=round(latency, 2),
                details=f"Collection '{QDRANT_COLLECTION_NAME}' not found",
                error="Collection needs to be created"
            ))
            non_critical_failures += 1
            logger.warning("Qdrant degraded | collection=%s not found", QDRANT_COLLECTION_NAME)

    except Exception as e:
        components.append(ComponentHealth(
            name="Qdrant Vector Database",
            status="unhealthy",
            details="Failed to connect to Qdrant",
            error=str(e)
        ))
        critical_failures += 1
        logger.exception("Qdrant unhealthy")

    # 2. Test BGE-M3 embedding generation
    logger.info("Checking BGE-M3 embeddings")
    try:
        start = time.time()
        test_text = "Testing embedding generation for health check"
        embedding = embeddings.embed_query(test_text)
        latency = (time.time() - start) * 1000

        if embedding and len(embedding) > 0:
            components.append(ComponentHealth(
                name="BGE-M3 Embeddings",
                status="healthy",
                latency_ms=round(latency, 2),
                details=f"Generated {len(embedding)}-dimensional embedding"
            ))
            logger.info("BGE-M3 healthy | latency_ms=%.2f", latency)
        else:
            components.append(ComponentHealth(
                name="BGE-M3 Embeddings",
                status="unhealthy",
                details="Embedding generation returned empty result",
                error="Empty embedding vector"
            ))
            critical_failures += 1
            logger.error("BGE-M3 unhealthy | empty embedding")

    except Exception as e:
        components.append(ComponentHealth(
            name="BGE-M3 Embeddings",
            status="unhealthy",
            details="Failed to generate embeddings",
            error=str(e)
        ))
        critical_failures += 1
        logger.exception("BGE-M3 unhealthy")

    # 3. Verify Gemini connectivity if configured
    if GEMINI_MODEL:
        logger.info("Checking Google Gemini API")
        if not os.getenv("GOOGLE_API_KEY"):
            components.append(ComponentHealth(
                name="Google Gemini API",
                status="degraded",
                details="GOOGLE_API_KEY is not configured",
                error="Missing GOOGLE_API_KEY"
            ))
            non_critical_failures += 1
        else:
            try:
                start = time.time()
                test_llm = build_chat_model("gemini", GEMINI_MODEL, temperature=0)
                test_response = test_llm.invoke([HumanMessage(content="Respond with OK")])
                latency = (time.time() - start) * 1000

                if test_response and test_response.content:
                    components.append(ComponentHealth(
                        name="Google Gemini API",
                        status="healthy",
                        latency_ms=round(latency, 2),
                        details=f"Successfully connected to {GEMINI_MODEL}"
                    ))
                    logger.info("Gemini healthy | latency_ms=%.2f", latency)
                else:
                    components.append(ComponentHealth(
                        name="Google Gemini API",
                        status="degraded",
                        latency_ms=round(latency, 2),
                        details="API responded but with empty content",
                        error="Empty response content"
                    ))
                    non_critical_failures += 1
                    logger.warning("Gemini degraded | empty response")

            except Exception as e:
                components.append(ComponentHealth(
                    name="Google Gemini API",
                    status="unhealthy",
                    details=f"Failed to connect to Gemini model {GEMINI_MODEL}",
                    error=str(e)
                ))
                critical_failures += 1
                logger.exception("Gemini unhealthy")

    # 4. Verify OpenAI connectivity if configured
    logger.info("Checking OpenAI API")
    if not OPENAI_API_KEY:
        components.append(ComponentHealth(
            name="OpenAI API",
            status="degraded",
            details="OPENAI_API_KEY is not configured",
            error="Missing OPENAI_API_KEY"
        ))
        non_critical_failures += 1
    else:
        try:
            start = time.time()
            test_llm = build_chat_model("openai", resolve_model_name("openai"), temperature=0)
            test_response = test_llm.invoke([HumanMessage(content="Respond with OK")])
            latency = (time.time() - start) * 1000

            if test_response and test_response.content:
                components.append(ComponentHealth(
                    name="OpenAI API",
                    status="healthy",
                    latency_ms=round(latency, 2),
                    details=f"Successfully connected to {resolve_model_name('openai')}"
                ))
                logger.info("OpenAI healthy | latency_ms=%.2f", latency)
            else:
                components.append(ComponentHealth(
                    name="OpenAI API",
                    status="degraded",
                    latency_ms=round(latency, 2),
                    details="API responded but with empty content",
                    error="Empty response content"
                ))
                non_critical_failures += 1
                logger.warning("OpenAI degraded | empty response")

        except Exception as e:
            components.append(ComponentHealth(
                name="OpenAI API",
                status="unhealthy",
                details=f"Failed to connect to OpenAI model {resolve_model_name('openai')}",
                error=str(e)
            ))
            critical_failures += 1
            logger.exception("OpenAI unhealthy")

    # 5. Test Tavily web search (if configured)
    logger.info("Checking Tavily web search")
    if TAVILY_API_KEY:
        try:
            start = time.time()
            from langchain_tavily import TavilySearch

            tavily_test = TavilySearch(
                max_results=1,
                topic="general"
            )

            # Simple test query
            test_result = tavily_test.invoke({"query": "test"})
            latency = (time.time() - start) * 1000

            if test_result:
                components.append(ComponentHealth(
                    name="Tavily Web Search",
                    status="healthy",
                    latency_ms=round(latency, 2),
                    details="Successfully executed test search"
                ))
                logger.info("Tavily healthy | latency_ms=%.2f", latency)
            else:
                components.append(ComponentHealth(
                    name="Tavily Web Search",
                    status="degraded",
                    latency_ms=round(latency, 2),
                    details="API responded but with empty results",
                    error="Empty search results"
                ))
                non_critical_failures += 1
                logger.warning("Tavily degraded | empty results")

        except Exception as e:
            components.append(ComponentHealth(
                name="Tavily Web Search",
                status="degraded",
                details="Failed to connect to Tavily API",
                error=str(e)
            ))
            non_critical_failures += 1
            logger.warning("Tavily degraded | error=%s", e)
    else:
        components.append(ComponentHealth(
            name="Tavily Web Search",
            status="degraded",
            details="Tavily API key not configured",
            error="TAVILY_API_KEY not set"
        ))
        non_critical_failures += 1
        logger.warning("Tavily degraded | not configured")

    # 5. Check DocumentProcessor initialization
    logger.info("Checking DocumentProcessor")
    try:
        start = time.time()

        # Verify document processor is initialized
        if document_processor:
            supported_formats = document_processor.supported_formats
            chunk_size = document_processor.chunk_size
            latency = (time.time() - start) * 1000

            components.append(ComponentHealth(
                name="DocumentProcessor",
                status="healthy",
                latency_ms=round(latency, 2),
                details=f"Initialized with {len(supported_formats)} supported formats, chunk_size={chunk_size}"
            ))
            logger.info("DocumentProcessor healthy | latency_ms=%.2f", latency)
        else:
            components.append(ComponentHealth(
                name="DocumentProcessor",
                status="unhealthy",
                details="DocumentProcessor not initialized",
                error="Processor instance is None"
            ))
            critical_failures += 1
            logger.error("DocumentProcessor unhealthy | not initialized")

    except Exception as e:
        components.append(ComponentHealth(
            name="DocumentProcessor",
            status="unhealthy",
            details="Failed to check DocumentProcessor",
            error=str(e)
        ))
        critical_failures += 1
        logger.exception("DocumentProcessor unhealthy")

    # Determine overall status
    if critical_failures > 0:
        overall_status = "unhealthy"
    elif non_critical_failures > 0:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    logger.info(
        "Health check complete | overall_status=%s | critical_failures=%s | non_critical_failures=%s",
        overall_status,
        critical_failures,
        non_critical_failures,
    )

    return SystemHealthResponse(
        overall_status=overall_status,
        timestamp=timestamp,
        components=components,
        summary={
            "total_components": len(components),
            "healthy": sum(1 for c in components if c.status == "healthy"),
            "degraded": sum(1 for c in components if c.status == "degraded"),
            "unhealthy": sum(1 for c in components if c.status == "unhealthy"),
            "critical_failures": critical_failures,
            "non_critical_failures": non_critical_failures
        }
    )


@app.post("/debug/embedding-test", response_model=EmbeddingTestResponse)
async def test_embeddings(request: EmbeddingTestRequest):
    """
    Test embedding generation and semantic similarity.

    This endpoint allows you to:
    - Test BGE-M3 embedding generation for custom texts
    - Verify embedding dimensions and quality
    - Compare semantic similarity between texts
    - Debug similarity computation issues

    Use Cases:
    - Test if similar texts produce high similarity scores
    - Verify embeddings are being generated correctly
    - Debug why certain queries don't match expected documents
    - Analyze semantic relationships between texts

    Example 1 - Basic embedding test:
        POST /debug/embedding-test
        {
            "texts": ["How to set stop loss?", "Stop loss configuration guide"],
            "compute_similarities": true
        }

    Example 2 - Compare against reference:
        POST /debug/embedding-test
        {
            "texts": ["Curriculum structure", "Course prerequisite information"],
            "reference_text": "How can I find curriculum details for the department?",
            "compute_similarities": false
        }
    """
    logger.info("Embedding test started | total_texts=%s", len(request.texts))

    try:
        start_time = time.time()

        # Step 1: Generate embeddings for all texts
        logger.info("Generating embeddings")
        try:
            embedding_start = time.time()
            text_embeddings = []

            for idx, text in enumerate(request.texts):
                embedding = embeddings.embed_query(text)
                text_embeddings.append(embedding)
                logger.info("Generated embedding | index=%s | dimensions=%s", idx + 1, len(embedding))

            # Generate reference embedding if provided
            reference_embedding = None
            if request.reference_text:
                reference_embedding = embeddings.embed_query(request.reference_text)
                logger.info("Generated reference embedding | dimensions=%s", len(reference_embedding))

            embedding_time = (time.time() - embedding_start) * 1000
            logger.info("All embeddings generated | latency_ms=%.2f", embedding_time)

        except Exception as e:
            logger.exception("Embedding generation error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate embeddings: {str(e)}"
            )

        # Step 2: Compute similarities if requested
        similarity_matrix = None

        if request.compute_similarities:
            logger.info("Computing similarity matrix")
            try:
                import numpy as np

                # Convert to numpy arrays for easier computation
                embeddings_array = np.array(text_embeddings)

                # Compute pairwise cosine similarities
                # Cosine similarity = dot product of normalized vectors
                norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
                normalized = embeddings_array / norms
                similarity_matrix = np.dot(normalized, normalized.T).tolist()

                logger.info("Computed similarity matrix | size=%sx%s", len(similarity_matrix), len(similarity_matrix))

            except Exception as e:
                logger.exception("Similarity computation error")
                # Don't fail the entire request, just skip similarity matrix
                similarity_matrix = None

        # Step 3: Compute similarity to reference if provided
        reference_similarities = []
        if reference_embedding:
            logger.info("Computing similarities to reference text")
            try:
                import numpy as np

                ref_array = np.array(reference_embedding)
                ref_norm = np.linalg.norm(ref_array)

                for text_emb in text_embeddings:
                    text_array = np.array(text_emb)
                    text_norm = np.linalg.norm(text_array)

                    # Cosine similarity
                    similarity = np.dot(ref_array, text_array) / (ref_norm * text_norm)
                    reference_similarities.append(float(similarity))

                logger.info("Computed reference similarities | total=%s", len(reference_similarities))

            except Exception as e:
                logger.exception("Reference similarity computation error")
                reference_similarities = [None] * len(request.texts)
        else:
            reference_similarities = [None] * len(request.texts)

        # Step 4: Build results
        results = []
        for idx, (text, embedding) in enumerate(zip(request.texts, text_embeddings)):
            result = EmbeddingResult(
                text=text,
                text_preview=text[:100] + ("..." if len(text) > 100 else ""),
                embedding_dimensions=len(embedding),
                similarity_to_reference=reference_similarities[idx]
            )
            results.append(result)

        total_time = (time.time() - start_time) * 1000

        logger.info("Embedding test completed | total_time_ms=%.2f", total_time)

        # Get embedding model name
        from src.backend.core.config import EMBED_MODEL

        return EmbeddingTestResponse(
            results=results,
            total_texts=len(request.texts),
            processing_time_ms=round(total_time, 2),
            embedding_model=EMBED_MODEL,
            similarity_matrix=similarity_matrix
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        logger.exception("Embedding test failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding test failed: {str(e)}"
        )
