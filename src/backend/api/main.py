import os
import time
from typing import List, Dict, Any, Optional
import uuid

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Query, Request
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Updated imports for new structure
from src.backend.core.agent import rag_agent, enhance_query_hero_bot_style
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
    QDRANT_COLLECTION_NAME,
    ENABLE_QUERY_ENHANCEMENT,
    GOOGLE_API_KEY,
    TAVILY_API_KEY,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_PER_MINUTE
)
from langchain_qdrant import QdrantVectorStore

# Initialize FastAPI app
app = FastAPI(
    title="HERO Bot RAG Agent API",
    description="API for HERO Bot - Finansia Hero Trading Platform assistant powered by Qdrant, Gemini, and BGE-M3.",
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

class AgentResponse(BaseModel):
    response: str
    trace_events: List[TraceEvent] = Field(default_factory=list)

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
            "similarity_threshold": body.similarity_threshold
        }

        final_message = ""

        print(f"--- Starting Agent Stream for session {body.session_id} ---")
        print(f"Web Search Enabled: {body.enable_web_search}") # For server-side debugging
        print(f"Force Web Search: {body.force_web_search}") # For server-side debugging
        print(f"Similarity Threshold: {body.similarity_threshold}") # For server-side debugging

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
                # Check for overridden route if web search was disabled
                initial_decision = node_output_state.get('initial_router_decision', route_decision)
                override_reason = node_output_state.get('router_override_reason', None)

                # NEW: HERO Bot Query Enhancement Information
                original_query = node_output_state.get('original_query', body.query)
                enhanced_query = node_output_state.get('enhanced_query', body.query)
                query_enhanced = enhanced_query != original_query and node_output_state.get('query_enhancement_enabled', False)

                if query_enhanced:
                    event_description = f"HERO Bot enhanced query and decided: '{route_decision}'"
                    event_details = {
                        "decision": route_decision,
                        "original_query": original_query,
                        "enhanced_query": enhanced_query,
                        "query_enhanced": True,
                        "reason": "Query enhanced for better trading platform search"
                    }
                elif override_reason:
                    event_description = f"Router initially decided: '{initial_decision}'. Overridden to: '{route_decision}' because {override_reason}."
                    event_details = {
                        "initial_decision": initial_decision,
                        "final_decision": route_decision,
                        "override_reason": override_reason,
                        "original_query": original_query,
                        "enhanced_query": enhanced_query,
                        "query_enhanced": query_enhanced
                    }
                else:
                    event_description = f"HERO Bot router decided: '{route_decision}'"
                    event_details = {
                        "decision": route_decision,
                        "reason": "Based on Finansia Hero trading platform analysis",
                        "original_query": original_query,
                        "enhanced_query": enhanced_query,
                        "query_enhanced": query_enhanced
                    }
                event_type = "hero_bot_routing"
            elif current_node_name == "rag_lookup":
                rag_content_summary = node_output_state.get("rag", "")[:200] + "..."
                rag_sufficient = node_output_state.get("route") == "answer"
                enhanced_query = node_output_state.get("enhanced_query", "")

                if rag_sufficient:
                    event_description = f"📚 Found relevant Finansia Hero platform documentation. Proceeding to answer."
                    event_details = {
                        "retrieved_content_summary": rag_content_summary,
                        "sufficiency_verdict": "Sufficient for trading platform question",
                        "enhanced_query": enhanced_query,
                        "search_type": "Platform Documentation Search"
                    }
                else:
                    event_description = f"📚 Platform docs found but not sufficient. Searching external trading resources."
                    event_details = {
                        "retrieved_content_summary": rag_content_summary,
                        "sufficiency_verdict": "Not sufficient - needs external resources",
                        "enhanced_query": enhanced_query,
                        "search_type": "Platform Documentation Search"
                    }

                event_type = "hero_bot_rag_search"
            elif current_node_name == "web_search":
                web_content_summary = node_output_state.get("web", "")[:200] + "..."
                enhanced_query = node_output_state.get("enhanced_query", "")

                if web_content_summary.startswith("Web search was disabled"):
                    event_description = f"🌐 Web search disabled by user. Using available information."
                    event_details = {
                        "search_status": "disabled",
                        "enhanced_query": enhanced_query,
                        "message": "External trading resource search was disabled by user preference"
                    }
                else:
                    event_description = f"🌐 Searched external trading resources. Results found from trusted financial sources."
                    event_details = {
                        "retrieved_content_summary": web_content_summary,
                        "enhanced_query": enhanced_query,
                        "search_domains": "www.finansiahero.com, smartaccess.fnsyrus.com",
                        "search_type": "External Trading Resources"
                    }
                event_type = "hero_bot_web_search"
            elif current_node_name == "answer":
                enhanced_query = node_output_state.get("enhanced_query", "")
                event_description = "🤖 HERO Bot generating specialized trading platform response."
                event_details = {
                    "bot_name": "HERO Bot",
                    "specialization": "Finansia Hero Trading Platform Assistant",
                    "enhanced_query": enhanced_query,
                    "response_type": "Trading Platform Specialized Response"
                }
                event_type = "hero_bot_response_generation"
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
            print(f"Streamed Event: Step {i+1} - Node: {current_node_name} - Desc: {event_description}")

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
             print("Agent finished, but no final AIMessage found in the final state after stream completion.")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Agent did not return a valid response (final AI message not found).")

        print(f"--- Agent Stream Ended. Final Response: {final_message[:200]}... ---")

        return AgentResponse(response=final_message, trace_events=trace_events_for_frontend)

    except Exception as e:
        import traceback
        traceback.print_exc()
        error_details = f"Error during agent invocation: {e}"
        print(error_details)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


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
    print(f"\n--- Retrieval Test Started ---")
    print(f"Query: {request.query}")
    print(f"Parameters: threshold={request.similarity_threshold}, top_k={request.top_k}")

    try:
        start_time = time.time()

        # Step 1: Test query enhancement if enabled
        original_query = request.query
        enhanced_query = None

        if ENABLE_QUERY_ENHANCEMENT:
            try:
                enhanced_query = enhance_query_hero_bot_style(original_query)
                print(f"Query enhanced: '{original_query}' -> '{enhanced_query}'")
            except Exception as e:
                print(f"Query enhancement failed: {e}")
                enhanced_query = original_query
        else:
            enhanced_query = original_query
            print("Query enhancement disabled")

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

            print(f"Retrieved {len(documents)} documents in {retrieval_latency:.2f}ms")

        except Exception as e:
            print(f"Retrieval error: {e}")
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
            print(f"Warning: Could not get collection stats: {e}")
            collection_stats = {"error": str(e)}

        total_time = (time.time() - start_time) * 1000

        print(f"--- Retrieval Test Completed in {total_time:.2f}ms ---")

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
        import traceback
        traceback.print_exc()
        print(f"Retrieval test error: {e}")
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
    - Google Gemini API connectivity
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
    print("\n--- Detailed Health Check Started ---")

    from datetime import datetime
    timestamp = datetime.now().isoformat()
    components: List[ComponentHealth] = []

    # Track critical component failures
    critical_failures = 0
    non_critical_failures = 0

    # 1. Check Qdrant connection and collection
    print("Checking Qdrant...")
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
            print(f"✓ Qdrant healthy ({latency:.2f}ms)")
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
            print(f"⚠ Qdrant degraded: collection not found")

    except Exception as e:
        components.append(ComponentHealth(
            name="Qdrant Vector Database",
            status="unhealthy",
            details="Failed to connect to Qdrant",
            error=str(e)
        ))
        critical_failures += 1
        print(f"✗ Qdrant unhealthy: {e}")

    # 2. Test BGE-M3 embedding generation
    print("Checking BGE-M3 embeddings...")
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
            print(f"✓ BGE-M3 healthy ({latency:.2f}ms)")
        else:
            components.append(ComponentHealth(
                name="BGE-M3 Embeddings",
                status="unhealthy",
                details="Embedding generation returned empty result",
                error="Empty embedding vector"
            ))
            critical_failures += 1
            print(f"✗ BGE-M3 unhealthy: empty embedding")

    except Exception as e:
        components.append(ComponentHealth(
            name="BGE-M3 Embeddings",
            status="unhealthy",
            details="Failed to generate embeddings",
            error=str(e)
        ))
        critical_failures += 1
        print(f"✗ BGE-M3 unhealthy: {e}")

    # 3. Verify Google Gemini API connectivity
    print("Checking Google Gemini API...")
    try:
        start = time.time()
        from langchain_google_genai import ChatGoogleGenerativeAI

        test_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY
        )

        # Simple test invocation
        test_response = test_llm.invoke([HumanMessage(content="Respond with 'OK'")])
        latency = (time.time() - start) * 1000

        if test_response and test_response.content:
            components.append(ComponentHealth(
                name="Google Gemini API",
                status="healthy",
                latency_ms=round(latency, 2),
                details="Successfully connected to gemini-2.5-flash"
            ))
            print(f"✓ Gemini healthy ({latency:.2f}ms)")
        else:
            components.append(ComponentHealth(
                name="Google Gemini API",
                status="degraded",
                latency_ms=round(latency, 2),
                details="API responded but with empty content",
                error="Empty response content"
            ))
            non_critical_failures += 1
            print(f"⚠ Gemini degraded: empty response")

    except Exception as e:
        components.append(ComponentHealth(
            name="Google Gemini API",
            status="unhealthy",
            details="Failed to connect to Gemini API",
            error=str(e)
        ))
        critical_failures += 1
        print(f"✗ Gemini unhealthy: {e}")

    # 4. Test Tavily web search (if configured)
    print("Checking Tavily web search...")
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
                print(f"✓ Tavily healthy ({latency:.2f}ms)")
            else:
                components.append(ComponentHealth(
                    name="Tavily Web Search",
                    status="degraded",
                    latency_ms=round(latency, 2),
                    details="API responded but with empty results",
                    error="Empty search results"
                ))
                non_critical_failures += 1
                print(f"⚠ Tavily degraded: empty results")

        except Exception as e:
            components.append(ComponentHealth(
                name="Tavily Web Search",
                status="degraded",
                details="Failed to connect to Tavily API",
                error=str(e)
            ))
            non_critical_failures += 1
            print(f"⚠ Tavily degraded: {e}")
    else:
        components.append(ComponentHealth(
            name="Tavily Web Search",
            status="degraded",
            details="Tavily API key not configured",
            error="TAVILY_API_KEY not set"
        ))
        non_critical_failures += 1
        print(f"⚠ Tavily degraded: not configured")

    # 5. Check DocumentProcessor initialization
    print("Checking DocumentProcessor...")
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
            print(f"✓ DocumentProcessor healthy ({latency:.2f}ms)")
        else:
            components.append(ComponentHealth(
                name="DocumentProcessor",
                status="unhealthy",
                details="DocumentProcessor not initialized",
                error="Processor instance is None"
            ))
            critical_failures += 1
            print(f"✗ DocumentProcessor unhealthy: not initialized")

    except Exception as e:
        components.append(ComponentHealth(
            name="DocumentProcessor",
            status="unhealthy",
            details="Failed to check DocumentProcessor",
            error=str(e)
        ))
        critical_failures += 1
        print(f"✗ DocumentProcessor unhealthy: {e}")

    # Determine overall status
    if critical_failures > 0:
        overall_status = "unhealthy"
    elif non_critical_failures > 0:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    print(f"\n--- Health Check Complete: {overall_status.upper()} ---")
    print(f"Critical failures: {critical_failures}, Non-critical failures: {non_critical_failures}")

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
            "texts": ["Trading platform features", "Account management"],
            "reference_text": "How to use the trading platform?",
            "compute_similarities": false
        }
    """
    print(f"\n--- Embedding Test Started ---")
    print(f"Testing {len(request.texts)} texts")

    try:
        start_time = time.time()

        # Step 1: Generate embeddings for all texts
        print("Generating embeddings...")
        try:
            embedding_start = time.time()
            text_embeddings = []

            for idx, text in enumerate(request.texts):
                embedding = embeddings.embed_query(text)
                text_embeddings.append(embedding)
                print(f"Generated embedding {idx+1}/{len(request.texts)}: {len(embedding)} dimensions")

            # Generate reference embedding if provided
            reference_embedding = None
            if request.reference_text:
                reference_embedding = embeddings.embed_query(request.reference_text)
                print(f"Generated reference embedding: {len(reference_embedding)} dimensions")

            embedding_time = (time.time() - embedding_start) * 1000
            print(f"All embeddings generated in {embedding_time:.2f}ms")

        except Exception as e:
            print(f"Embedding generation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate embeddings: {str(e)}"
            )

        # Step 2: Compute similarities if requested
        similarity_matrix = None

        if request.compute_similarities:
            print("Computing similarity matrix...")
            try:
                import numpy as np

                # Convert to numpy arrays for easier computation
                embeddings_array = np.array(text_embeddings)

                # Compute pairwise cosine similarities
                # Cosine similarity = dot product of normalized vectors
                norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
                normalized = embeddings_array / norms
                similarity_matrix = np.dot(normalized, normalized.T).tolist()

                print(f"Computed {len(similarity_matrix)}x{len(similarity_matrix)} similarity matrix")

            except Exception as e:
                print(f"Similarity computation error: {e}")
                # Don't fail the entire request, just skip similarity matrix
                similarity_matrix = None

        # Step 3: Compute similarity to reference if provided
        reference_similarities = []
        if reference_embedding:
            print("Computing similarities to reference text...")
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

                print(f"Computed {len(reference_similarities)} reference similarities")

            except Exception as e:
                print(f"Reference similarity computation error: {e}")
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

        print(f"--- Embedding Test Completed in {total_time:.2f}ms ---")

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
        import traceback
        traceback.print_exc()
        print(f"Embedding test error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding test failed: {str(e)}"
        )