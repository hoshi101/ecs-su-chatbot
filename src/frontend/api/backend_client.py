import requests
import json

def upload_document_to_backend(fastapi_base_url: str, uploaded_file):
    """
    Sends a PDF document to the FastAPI backend for upload and indexing.

    Args:
        fastapi_base_url (str): The base URL of the FastAPI backend.
        uploaded_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The file object from Streamlit's file_uploader.

    Returns:
        dict: The JSON response from the backend on success.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
        json.JSONDecodeError: If the response is not valid JSON.
    """
    # Prepare the file for a multipart/form-data request
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

    # Make a POST request to the backend's upload endpoint
    response = requests.post(f"{fastapi_base_url}/upload-document/", files=files)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

    return response.json()

def extract_enhancement_info(trace_events):
    """
    Extract query enhancement information from trace events.

    Args:
        trace_events (list): List of trace events from the backend.

    Returns:
        dict or None: Enhancement information if found.
    """
    for event in trace_events:
        if hasattr(event, 'details') and event.details:
            details = event.details
            if details.get("original_query") and details.get("enhanced_query"):
                return {
                    "original_query": details.get("original_query"),
                    "enhanced_query": details.get("enhanced_query"),
                    "enhancement_reason": details.get("enhancement_reason", "Query was enhanced for better search results")
                }
    return None


def extract_source_documents(trace_events):
    """
    Extract source document information from trace events.

    Args:
        trace_events (list): List of trace events from the backend.

    Returns:
        list: List of source documents with metadata.
    """
    source_docs = []

    for event in trace_events:
        if hasattr(event, 'details') and event.details:
            details = event.details

            # Check for retrieved documents
            if details.get("retrieved_documents"):
                docs = details["retrieved_documents"]
                if isinstance(docs, list):
                    for doc in docs:
                        source_docs.append({
                            "title": doc.get("title", "Document"),
                            "snippet": doc.get("content", "")[:300],  # First 300 chars
                            "relevance_score": doc.get("score", 0.0),
                            "source_type": doc.get("source", "Internal Knowledge Base")
                        })

            # Check for search results
            elif details.get("search_results"):
                results = details["search_results"]
                if isinstance(results, list):
                    for result in results:
                        source_docs.append({
                            "title": result.get("title", "Search Result"),
                            "snippet": result.get("snippet", ""),
                            "relevance_score": result.get("relevance", 0.0),
                            "source_type": "Official Website Search",
                            "url": result.get("url", "")
                        })

            # Check for retrieved content summary
            elif details.get("retrieved_content_summary"):
                source_docs.append({
                    "title": "Retrieved Content",
                    "snippet": details["retrieved_content_summary"],
                    "relevance_score": 0.8,  # Default score
                    "source_type": "Department Knowledge Base"
                })

    return source_docs


def chat_with_backend_agent(fastapi_base_url: str, session_id: str, query: str, enable_web_search: bool,
                           force_web_search: bool = False, similarity_threshold: float = 0.7):
    """
    Sends a chat query to the FastAPI backend's agent.

    Args:
        fastapi_base_url (str): The base URL of the FastAPI backend.
        session_id (str): Unique ID for the current chat session.
        query (str): The user's chat message.
        enable_web_search (bool): Flag indicating if web search is enabled.
        force_web_search (bool): Flag to force web search regardless of routing.
        similarity_threshold (float): Threshold for search relevance (0.0-1.0).

    Returns:
        tuple: (agent_response_text: str, trace_events: list, enhancement_info: dict, source_docs: list)

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
        json.JSONDecodeError: If the response is not valid JSON.
    """
    payload = {
        "session_id": session_id,
        "query": query,
        "enable_web_search": enable_web_search or force_web_search,
        "force_web_search": force_web_search,
        "similarity_threshold": similarity_threshold
    }

    response = requests.post(f"{fastapi_base_url}/chat/", json=payload, stream=False)
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

    data = response.json()
    agent_response = data.get("response", "Sorry, I couldn't get a response from the agent.")
    trace_events = data.get("trace_events", [])

    # Extract enhancement and source information
    enhancement_info = extract_enhancement_info(trace_events)
    source_docs = extract_source_documents(trace_events)

    return agent_response, trace_events, enhancement_info, source_docs
