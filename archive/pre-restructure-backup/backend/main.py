import os
import time
from typing import List, Dict, Any
import tempfile

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.document_loaders import PyPDFLoader



from backend.agent import rag_agent
from backend.vectorstore import add_document_to_vectorstore

# Initialize FastAPI app
app = FastAPI(
    title="HERO Bot RAG Agent API",
    description="API for HERO Bot - Finansia Hero Trading Platform assistant powered by Qdrant, Gemini, and BGE-M3.",
    version="2.0.0",
)

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

class AgentResponse(BaseModel):
    response: str
    trace_events: List[TraceEvent] = Field(default_factory=list)

class DocumentUploadResponse(BaseModel):
    message: str
    filename: str
    processed_chunks: int

# --- Document Upload Endpoint ---
@app.post("/upload-document/", response_model=DocumentUploadResponse, status_code=status.HTTP_200_OK)
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads a PDF document, extracts text, and adds it to the RAG knowledge base.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        file_content = await file.read()
        tmp_file.write(file_content)
        temp_file_path = tmp_file.name
    
    print(f"Received PDF for upload: {file.filename}. Saved temporarily to {temp_file_path}")

    try:
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()

        total_chunks_added = 0
        if documents:
            full_text_content = "\n\n".join([doc.page_content for doc in documents])
            add_document_to_vectorstore(full_text_content)
            total_chunks_added = len(documents)
        
        return DocumentUploadResponse(
            message=f"PDF '{file.filename}' successfully uploaded and indexed.",
            filename=file.filename,
            processed_chunks=total_chunks_added
        )
    except Exception as e:
        print(f"Error processing PDF document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {e}"
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")



# --- Chat Endpoint ---
@app.post("/chat/", response_model=AgentResponse)
async def chat_with_agent(request: QueryRequest):
    trace_events_for_frontend: List[TraceEvent] = []
    
    try:
        # Pass enable_web_search into the config for the agent to access
        config = {
            "configurable": {
                "thread_id": request.session_id,
                "web_search_enabled": request.enable_web_search
            }
        }
        inputs = {"messages": [HumanMessage(content=request.query)]}

        final_message = ""
        
        print(f"--- Starting Agent Stream for session {request.session_id} ---")
        print(f"Web Search Enabled: {request.enable_web_search}") # For server-side debugging

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
                original_query = node_output_state.get('original_query', request.query)
                enhanced_query = node_output_state.get('enhanced_query', request.query)
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