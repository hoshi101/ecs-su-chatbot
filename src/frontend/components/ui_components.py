from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from config.settings import FRONTEND_CONFIG

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def display_header():
    """Display the application header with title and description."""
    st.title(FRONTEND_CONFIG["BOT_NAME"])
    st.caption(f"English name: {FRONTEND_CONFIG['BOT_NAME_EN']}")
    st.markdown(
        """
    **ผู้ช่วยข้อมูลของสาขาวิชาวิศวกรรมอิเล็กทรอนิกส์และระบบคอมพิวเตอร์ / วิศวกรรมไฟฟ้า**

    ระบบนี้ช่วยตอบคำถามจากข้อมูลทางการของภาควิชา เช่น
    - หลักสูตรและรายวิชา
    - อาจารย์และบุคลากร
    - ระเบียบการศึกษาและขั้นตอนทั่วไป
    - ฝึกงาน สหกิจศึกษา และบริการนักศึกษา
    - ข้อมูลติดต่อภาควิชา
    """
    )
    st.divider()


def render_sidebar_settings():
    """Render the sidebar with settings and controls."""
    with st.sidebar:
        st.header("Settings")

        if st.button("Clear Conversation", use_container_width=True):
            from state.session_manager import clear_conversation

            clear_conversation()
            st.rerun()

        st.divider()

        provider_options = st.session_state.get("llm_options", {}) or {}
        provider_names = list(provider_options.keys()) or ["gemini", "openai"]
        current_provider = st.session_state.get("llm_provider", provider_names[0])
        if current_provider not in provider_names:
            current_provider = provider_names[0]

        provider_index = provider_names.index(current_provider)
        selected_provider = st.selectbox(
            "LLM Provider",
            options=provider_names,
            index=provider_index,
            format_func=lambda value: value.capitalize(),
            help="Choose which API provider should answer this conversation.",
        )
        st.session_state.llm_provider = selected_provider

        suggested_models = provider_options.get(selected_provider) or []
        current_model = st.session_state.get("llm_model", "")
        if suggested_models and current_model not in suggested_models:
            current_model = suggested_models[0]
            st.session_state.llm_model = current_model
        model_choices = suggested_models + ["custom"]
        default_choice = current_model if current_model in suggested_models else "custom"
        selected_model_choice = st.selectbox(
            "Model Preset",
            options=model_choices,
            index=model_choices.index(default_choice),
            format_func=lambda value: "Custom" if value == "custom" else value,
            help="Pick a recommended model preset or switch to Custom to type a specific model name.",
        )

        custom_default_value = current_model
        if selected_model_choice == "custom":
            typed_model = st.text_input(
                "Custom Model Name",
                value=custom_default_value,
                help="Example: gemini-2.5-flash or chat-latest",
            ).strip()
            st.session_state.llm_model = typed_model
        else:
            st.session_state.llm_model = selected_model_choice

        active_model = st.session_state.get("llm_model", "")
        if active_model:
            st.caption(f"Active model: {selected_provider}/{active_model}")
        else:
            st.warning("Please choose or type a model name before sending a message.")

        st.divider()

        similarity_threshold = st.slider(
            "Search Relevance",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get("similarity_threshold", 0.7),
            step=0.05,
            help="Higher values require more relevant matches. Lower values may retrieve broader results.",
        )
        st.session_state.similarity_threshold = similarity_threshold

        web_search_enabled = st.checkbox(
            "Enable Official Website Search",
            value=st.session_state.get("web_search_enabled", True),
            help="Allow fallback search on official department/faculty websites when the local knowledge base is insufficient.",
        )
        st.session_state.web_search_enabled = web_search_enabled

        if web_search_enabled:
            st.success("Official website fallback enabled")
        else:
            st.warning("Official website fallback disabled")

        st.caption("Trusted domains: ee-eng.su.ac.th, eng2.su.ac.th")


def render_agent_settings_section():
    """Render the agent settings section (deprecated - moved to sidebar)."""
    pass


def render_force_web_search_toggle():
    """Render force web search toggle next to chat input."""
    force_web_search = st.toggle(
        "Force web search",
        value=st.session_state.get("force_web_search", False),
        help="Force official website fallback search",
    )
    st.session_state.force_web_search = force_web_search
    return force_web_search


def display_query_enhancement():
    """Display query enhancement information if available."""
    if st.session_state.get("enhanced_query"):
        enhancement_data = st.session_state.enhanced_query

        with st.expander("Query Enhancement", expanded=False):
            st.markdown("**Original Query:**")
            st.code(enhancement_data.get("original_query", ""), language="text")

            st.markdown("**Enhanced Query:**")
            st.code(enhancement_data.get("enhanced_query", ""), language="text")

            if enhancement_data.get("enhancement_reason"):
                st.markdown("**Enhancement Reason:**")
                st.info(enhancement_data["enhancement_reason"])


def _render_source_file_access(doc: Dict[str, Any], index: int) -> None:
    file_path = doc.get("file_path")
    if not file_path:
        return

    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    st.caption(f"File path: {path}")

    if not path.exists() or not path.is_file():
        return

    if path.suffix.lower() not in {".pdf", ".md", ".txt", ".json", ".csv"}:
        return

    with path.open("rb") as handle:
        st.download_button(
            label="Download source file",
            data=handle.read(),
            file_name=path.name,
            mime="application/octet-stream",
            key=f"download-source-{index}-{path.name}",
            use_container_width=True,
        )


def display_source_documents():
    """Display source documents information if available."""
    if st.session_state.get("source_documents"):
        source_docs: List[Dict[str, Any]] = st.session_state.source_documents

        with st.expander("Source Documents", expanded=False):
            st.markdown(f"**Found {len(source_docs)} relevant sources:**")

            for i, doc in enumerate(source_docs, 1):
                with st.container():
                    st.markdown(f"**{i}. {doc.get('title', 'Untitled Document')}**")

                    if doc.get("snippet"):
                        st.markdown(doc["snippet"])

                    meta_parts = []
                    if doc.get("source_type"):
                        meta_parts.append(f"Type: {doc['source_type']}")
                    if doc.get("file_name"):
                        meta_parts.append(f"File: {doc['file_name']}")
                    if doc.get("page_label"):
                        meta_parts.append(f"Page: {doc['page_label']}")
                    elif doc.get("page") is not None:
                        meta_parts.append(f"Page: {doc['page']}")
                    if doc.get("chunk_index") is not None and doc.get("total_chunks") is not None:
                        meta_parts.append(f"Chunk: {doc['chunk_index'] + 1}/{doc['total_chunks']}")
                    if doc.get("relevance_score") is not None:
                        try:
                            meta_parts.append(f"Score: {float(doc['relevance_score']):.4f}")
                        except (TypeError, ValueError):
                            meta_parts.append(f"Score: {doc['relevance_score']}")

                    if meta_parts:
                        st.caption(" | ".join(meta_parts))

                    if doc.get("source_url"):
                        st.markdown(f"Source URL: {doc['source_url']}")

                    _render_source_file_access(doc, i)

                    if i < len(source_docs):
                        st.divider()


def display_chat_history():
    """Display the chat history from session state."""
    if "messages" not in st.session_state:
        return

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def display_trace_events(trace_events):
    """Display the agent workflow trace events."""
    if not trace_events:
        return

    with st.expander("Assistant Workflow Trace", expanded=False):
        st.markdown("See how the assistant processed your question:")

        for i, event in enumerate(trace_events, 1):
            event_type = event.get("event_type", "generic_node_execution")
            step = event.get("step", i)
            description = event.get("description", "")
            details = event.get("details", {}) or {}
            node_name = event.get("node_name", "node")

            with st.container():
                if event_type == "routing":
                    st.markdown(f"**Step {step}: Router Decision**")
                elif event_type == "rag_search":
                    st.markdown(f"**Step {step}: Knowledge Base Search**")
                elif event_type == "web_search":
                    st.markdown(f"**Step {step}: Official Website Search**")
                elif event_type == "response_generation":
                    st.markdown(f"**Step {step}: Response Generation**")
                else:
                    st.markdown(f"**Step {step}: {node_name}**")

                st.markdown(f"_{description}_")

                if details:
                    with st.expander("Details", expanded=False):
                        for key, value in details.items():
                            if key == "query_enhanced" and value:
                                st.success("Query was enhanced for better search results")
                            elif key in {"retrieved_documents", "search_results"} and isinstance(value, list):
                                st.caption(f"{key}: {len(value)} item(s)")
                            else:
                                st.text(f"{key}: {value}")

                if i < len(trace_events):
                    st.markdown("↓")

        st.markdown("---")
        st.caption("This trace shows routing, retrieval, and response-generation steps for debugging and transparency.")
