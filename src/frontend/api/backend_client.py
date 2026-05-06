import json
from typing import Any, Dict, List

import requests


def upload_document_to_backend(fastapi_base_url: str, uploaded_file):
    """
    Sends a PDF document to the FastAPI backend for upload and indexing.
    """
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    response = requests.post(f"{fastapi_base_url}/upload-document/", files=files)
    response.raise_for_status()
    return response.json()


def _get_event_attr(event: Any, key: str, default=None):
    if isinstance(event, dict):
        return event.get(key, default)
    return getattr(event, key, default)


def normalize_trace_events(trace_events: List[Any]) -> List[Dict[str, Any]]:
    normalized = []
    for event in trace_events or []:
        normalized.append(
            {
                "step": _get_event_attr(event, "step"),
                "node_name": _get_event_attr(event, "node_name"),
                "description": _get_event_attr(event, "description", ""),
                "details": _get_event_attr(event, "details", {}) or {},
                "event_type": _get_event_attr(event, "event_type", "generic_node_execution"),
            }
        )
    return normalized


def extract_enhancement_info(trace_events: List[Dict[str, Any]]):
    """
    Extract query enhancement information from trace events.
    """
    for event in trace_events:
        details = event.get("details", {})
        if details.get("original_query") and details.get("enhanced_query"):
            if details["original_query"] != details["enhanced_query"]:
                return {
                    "original_query": details.get("original_query"),
                    "enhanced_query": details.get("enhanced_query"),
                    "enhancement_reason": details.get(
                        "enhancement_reason",
                        details.get("reason", "Query was enhanced for better search results"),
                    ),
                }
    return None


def extract_source_documents(trace_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Backward-compatible extraction when the backend does not send a dedicated sources list.
    """
    source_docs = []

    for event in trace_events:
        details = event.get("details", {})
        for doc in details.get("retrieved_documents", []):
            source_docs.append(
                {
                    "title": doc.get("title", "Document"),
                    "snippet": doc.get("snippet") or doc.get("content", "")[:300],
                    "relevance_score": doc.get("relevance_score", doc.get("score")),
                    "source_type": doc.get("source_type", "Department Knowledge Base"),
                    "source_url": doc.get("source_url") or doc.get("url"),
                    "file_name": doc.get("file_name"),
                    "file_path": doc.get("file_path"),
                    "page": doc.get("page"),
                    "page_label": doc.get("page_label"),
                    "chunk_index": doc.get("chunk_index"),
                    "total_chunks": doc.get("total_chunks"),
                }
            )

        for result in details.get("search_results", []):
            source_docs.append(
                {
                    "title": result.get("title", "Search Result"),
                    "snippet": result.get("snippet", ""),
                    "relevance_score": result.get("relevance_score", result.get("relevance")),
                    "source_type": result.get("source_type", "Official Website Search"),
                    "source_url": result.get("source_url") or result.get("url"),
                }
            )

    return source_docs


def get_llm_options(fastapi_base_url: str) -> Dict[str, Any]:
    response = requests.get(f"{fastapi_base_url}/llm/options")
    response.raise_for_status()
    return response.json()


def chat_with_backend_agent(
    fastapi_base_url: str,
    session_id: str,
    query: str,
    enable_web_search: bool,
    llm_provider: str,
    llm_model: str,
    force_web_search: bool = False,
    similarity_threshold: float = 0.7,
):
    """
    Sends a chat query to the FastAPI backend's agent.
    """
    payload = {
        "session_id": session_id,
        "query": query,
        "enable_web_search": enable_web_search or force_web_search,
        "force_web_search": force_web_search,
        "similarity_threshold": similarity_threshold,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
    }

    response = requests.post(f"{fastapi_base_url}/chat/", json=payload, stream=False)
    response.raise_for_status()

    data = response.json()
    agent_response = data.get("response", "Sorry, I couldn't get a response from the agent.")
    trace_events = normalize_trace_events(data.get("trace_events", []))

    enhancement_info = extract_enhancement_info(trace_events)
    source_docs = data.get("sources") or extract_source_documents(trace_events)

    return agent_response, trace_events, enhancement_info, source_docs
