import streamlit as st
def display_header():
    """Display the application header with title and description."""
    st.title("EE Support Assistant")
    st.markdown("""
    **ผู้ช่วยข้อมูลของสาขาวิชาวิศวกรรมอิเล็กทรอนิกส์และระบบคอมพิวเตอร์ / วิศวกรรมไฟฟ้า**

    ระบบนี้ช่วยตอบคำถามจากข้อมูลทางการของภาควิชา เช่น
    - หลักสูตรและรายวิชา
    - อาจารย์และบุคลากร
    - ระเบียบการศึกษาและขั้นตอนทั่วไป
    - ฝึกงาน สหกิจศึกษา และบริการนักศึกษา
    - ข้อมูลติดต่อภาควิชา
    """)
    st.divider()



def render_sidebar_settings():
    """Render the sidebar with settings and controls."""
    with st.sidebar:
        st.header("⚙️ Settings")

        if st.button("🗑️ Clear Conversation", use_container_width=True):
            from state.session_manager import clear_conversation
            clear_conversation()
            st.rerun()

        st.divider()

        # Search relevance slider
        similarity_threshold = st.slider(
            "Search Relevance",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get("similarity_threshold", 0.7),
            step=0.05,
            help="Higher values require more relevant matches. Lower values may retrieve broader results."
        )
        st.session_state.similarity_threshold = similarity_threshold

        web_search_enabled = st.checkbox(
            "Enable Official Website Search",
            value=st.session_state.get("web_search_enabled", True),
            help="Allow fallback search on official department/faculty websites when the local knowledge base is insufficient."
        )
        st.session_state.web_search_enabled = web_search_enabled

        if web_search_enabled:
            st.success("🌐 Official website fallback enabled")
        else:
            st.warning("🔒 Website fallback disabled")

        st.caption("Trusted domains: ee-eng.su.ac.th, eng2.su.ac.th")


def render_agent_settings_section():
    """Render the agent settings section (deprecated - moved to sidebar)."""
    # This function is kept for backward compatibility but functionality moved to sidebar
    pass


def render_force_web_search_toggle():
    """Render force web search toggle next to chat input."""
    force_web_search = st.toggle(
        '🌐',
        value=st.session_state.get("force_web_search", False),
        help="Force official website fallback search"
    )
    st.session_state.force_web_search = force_web_search
    return force_web_search


def display_query_enhancement():
    """Display query enhancement information if available."""
    if st.session_state.get("enhanced_query"):
        enhancement_data = st.session_state.enhanced_query

        with st.expander("✨ Query Enhancement", expanded=False):
            st.markdown("**Original Query:**")
            st.code(enhancement_data.get("original_query", ""), language="text")

            st.markdown("**Enhanced Query:**")
            st.code(enhancement_data.get("enhanced_query", ""), language="text")

            if enhancement_data.get("enhancement_reason"):
                st.markdown("**Enhancement Reason:**")
                st.info(enhancement_data["enhancement_reason"])


def display_source_documents():
    """Display source documents information if available."""
    if st.session_state.get("source_documents"):
        source_docs = st.session_state.source_documents

        with st.expander("📚 Source Documents", expanded=False):
            st.markdown(f"**Found {len(source_docs)} relevant sources:**")

            for i, doc in enumerate(source_docs, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**{i}. {doc.get('title', 'Untitled Document')}**")
                        if doc.get('snippet'):
                            snippet = doc["snippet"][:220]
                            st.markdown(f"*{snippet}...*" if len(doc["snippet"]) > 220 else f"*{snippet}*")

                    with col2:
                        if doc.get('relevance_score'):
                            score = float(doc['relevance_score'])
                            st.metric("Relevance", f"{score:.2f}")

                    if doc.get('source_type'):
                        st.caption(f"Source: {doc['source_type']}")

                    if doc.get('url'):
                        st.caption(f"URL: {doc['url']}")

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

    with st.expander("🔍 Assistant Workflow Trace", expanded=False):
        st.markdown("See how the assistant processed your question:")

        for i, event in enumerate(trace_events, 1):
            # Create a container for each event
            with st.container():
                # Color-code based on event type
                if event.event_type == "routing":
                    st.markdown(f"**🎯 Step {event.step}: Router Decision**")
                elif event.event_type == "rag_search":
                    st.markdown(f"**📚 Step {event.step}: Knowledge Base Search**")
                elif event.event_type == "web_search":
                    st.markdown(f"**🌐 Step {event.step}: Official Website Search**")
                elif event.event_type == "response_generation":
                    st.markdown(f"**🤖 Step {event.step}: Response Generation**")
                else:
                    st.markdown(f"**⚙️ Step {event.step}: {event.node_name}**")

                st.markdown(f"_{event.description}_")

                # Show additional details if available
                if event.details:
                    with st.expander("Details", expanded=False):
                        # Format details nicely
                        for key, value in event.details.items():
                            if key == "query_enhanced" and value:
                                st.success("✨ Query was enhanced for better search results")
                            elif key == "original_query":
                                st.text(f"Original: {value}")
                            elif key == "enhanced_query":
                                st.text(f"Enhanced: {value}")
                            elif key == "decision":
                                st.info(f"Decision: {value}")
                            elif key == "search_domains":
                                st.text(f"Search domains: {value}")
                            elif key == "retrieved_content_summary":
                                st.text(f"Content summary: {value}")
                            else:
                                st.text(f"{key}: {value}")

                if i < len(trace_events):
                    st.markdown("↓")

        st.markdown("---")
        st.caption("This trace shows the assistant's retrieval and routing process for transparency and debugging.")
