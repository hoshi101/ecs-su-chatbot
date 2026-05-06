import streamlit as st
import requests
import json
from config.settings import FRONTEND_CONFIG
from state.session_manager import init_session_state
from components.ui_components import (
    display_header,
    render_sidebar_settings,
    render_force_web_search_toggle,
    display_chat_history,
    display_query_enhancement,
    display_source_documents,
    display_trace_events
)
from api.backend_client import chat_with_backend_agent, get_llm_options

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
                "openai": ["chat-latest", "gpt-5.5", "gpt-5.4", "gpt-5.4-mini", "gpt-4.1"],
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
            with st.spinner("Assistant is preparing an answer..."):
                try:
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

                    # Store enhancement and source information in session state
                    st.session_state.enhanced_query = enhancement_info
                    st.session_state.source_documents = source_docs
                    st.session_state.trace_events = trace_events

                    # Display the agent's final response
                    st.markdown(agent_response)
                    # Add the agent's response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": agent_response})

                    # Display the workflow trace
                    display_trace_events(trace_events)

                    # Display enhancement and source info immediately after response
                    if enhancement_info:
                        display_query_enhancement()
                    if source_docs:
                        display_source_documents()

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
