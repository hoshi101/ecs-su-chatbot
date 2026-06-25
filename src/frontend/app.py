import streamlit as st
import requests
import json
import time
from src.frontend.config.settings import FRONTEND_CONFIG
from src.frontend.state.session_manager import init_session_state
from src.frontend.components.ui_components import (
    display_header,
    render_sidebar_settings,
    render_force_web_search_toggle,
    display_chat_history,
    display_query_enhancement,
    display_source_documents,
    display_trace_events
)
from src.frontend.api.backend_client import chat_with_backend_agent, get_llm_options


def apply_minimum_response_delay(trace_events, started_at: float) -> None:
    elapsed = time.monotonic() - started_at
    first_event = trace_events[0] if trace_events else {}
    details = first_event.get("details", {}) if isinstance(first_event, dict) else {}
    is_shortcut = bool(details.get("shortcut_type"))

    target_delay = (
        FRONTEND_CONFIG["MIN_SHORTCUT_RESPONSE_SECONDS"]
        if is_shortcut
        else FRONTEND_CONFIG["MIN_STANDARD_RESPONSE_SECONDS"]
    )
    remaining_delay = target_delay - elapsed
    if remaining_delay > 0:
        time.sleep(remaining_delay)

def main():
    """Main function to run the Streamlit application."""

    # Initialize session state variables
    init_session_state()

    # Get FastAPI base URL from config
    fastapi_base_url = FRONTEND_CONFIG["FASTAPI_BASE_URL"]

    if not st.session_state.get("llm_options"):
        try:
            llm_options_payload = get_llm_options(fastapi_base_url)
            st.session_state.llm_options = llm_options_payload.get("providers", {})
            st.session_state.llm_provider = llm_options_payload.get(
                "default_provider",
                st.session_state.get("llm_provider", FRONTEND_CONFIG["DEFAULT_LLM_PROVIDER"]),
            )
            st.session_state.llm_model = llm_options_payload.get(
                "default_model",
                st.session_state.get("llm_model", FRONTEND_CONFIG["DEFAULT_LLM_MODEL"]),
            )
        except requests.exceptions.RequestException:
            st.session_state.llm_options = {
                "gemini": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
                "openai": ["gpt-5.4-mini", "gpt-5.4", "gpt-5.5", "chat-latest", "gpt-4.1"],
            }

    # Render sidebar with settings
    render_sidebar_settings()

    # Render main UI sections
    display_header()

    st.header(f"Chat with {FRONTEND_CONFIG['BOT_NAME']}")
    display_chat_history()

    # Display diagnostics from the previous interaction
    display_query_enhancement()
    display_source_documents()
    display_trace_events(st.session_state.get("trace_events", []))

    # Force web search toggle above chat input
    col1, col2 = st.columns([3, 1])
    with col2:
        force_web_search = render_force_web_search_toggle()

    # User input field
    if prompt := st.chat_input("Ask about curriculum, lecturers, regulations, or department contact information"):
        # Add user's message to chat history and display immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant's response and trace
        with st.chat_message("assistant"):
            with st.spinner("กำลังค้นข้อมูลจากเอกสารทางการและเรียบเรียงคำตอบ..."):
                try:
                    request_started_at = time.monotonic()
                    # Call the backend API for chat with enhanced parameters
                    agent_response, trace_events, enhancement_info, source_docs = chat_with_backend_agent(
                        fastapi_base_url,
                        st.session_state.session_id,
                        prompt,
                        st.session_state.web_search_enabled,
                        st.session_state.llm_provider,
                        st.session_state.llm_model,
                        force_web_search,
                        st.session_state.similarity_threshold
                    )
                    apply_minimum_response_delay(trace_events, request_started_at)

                    # Store enhancement and source information in session state
                    st.session_state.enhanced_query = enhancement_info
                    st.session_state.source_documents = source_docs
                    st.session_state.trace_events = trace_events

                    # Display the agent's final response
                    st.markdown(agent_response)
                    # Add the agent's response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": agent_response})
                    st.rerun()

                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the FastAPI backend. Please ensure it's running.")
                    st.session_state.messages.append({"role": "assistant", "content": "Error: Could not connect to the backend."})
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred with the request: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
                except json.JSONDecodeError:
                    st.error("Received an invalid response from the backend.")
                    st.session_state.messages.append({"role": "assistant", "content": "Error: Invalid response from backend."})
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Unexpected Error: {e}"})

if __name__ == "__main__":
    main()
