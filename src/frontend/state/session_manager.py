import streamlit as st
import uuid
from config.settings import FRONTEND_CONFIG

def init_session_state():
    """
    Initializes necessary variables in Streamlit's session state.
    This ensures data persists across reruns of the Streamlit app.
    """
    # Initialize chat message history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize a unique session ID for LangGraph checkpointing and conversation tracking
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                f"สวัสดีครับ ผมคือ {FRONTEND_CONFIG['BOT_NAME']} "
                "ยินดีช่วยตอบคำถามเกี่ยวกับหลักสูตร รายวิชา อาจารย์ ระเบียบการศึกษา "
                "และข้อมูลติดต่อของภาควิชาครับ"
            ),
        })

    # Initialize the web search enabled flag, defaulting to True
    if "web_search_enabled" not in st.session_state:
        st.session_state.web_search_enabled = True

    if "llm_options" not in st.session_state:
        st.session_state.llm_options = {}

    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = FRONTEND_CONFIG.get("DEFAULT_LLM_PROVIDER", "gemini")

    if "llm_model" not in st.session_state:
        st.session_state.llm_model = FRONTEND_CONFIG.get("DEFAULT_LLM_MODEL", "gemini-2.5-flash")

    # Initialize similarity threshold for search relevance (0.0-1.0, default 0.7)
    if "similarity_threshold" not in st.session_state:
        st.session_state.similarity_threshold = 0.7

    # Initialize force web search toggle
    if "force_web_search" not in st.session_state:
        st.session_state.force_web_search = False

    # Initialize enhanced query tracking
    if "enhanced_query" not in st.session_state:
        st.session_state.enhanced_query = None

    # Initialize source documents tracking
    if "source_documents" not in st.session_state:
        st.session_state.source_documents = []

    if "trace_events" not in st.session_state:
        st.session_state.trace_events = []


def clear_conversation():
    """
    Clear the conversation history and reset session state.
    Generates a new session ID while preserving settings.
    """
    # Preserve settings
    web_search_enabled = st.session_state.get("web_search_enabled", True)
    similarity_threshold = st.session_state.get("similarity_threshold", 0.7)
    force_web_search = st.session_state.get("force_web_search", False)
    llm_provider = st.session_state.get("llm_provider", FRONTEND_CONFIG.get("DEFAULT_LLM_PROVIDER", "gemini"))
    llm_model = st.session_state.get("llm_model", FRONTEND_CONFIG.get("DEFAULT_LLM_MODEL", "gemini-2.5-flash"))

    # Clear conversation-specific state
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.enhanced_query = None
    st.session_state.source_documents = []
    st.session_state.trace_events = []

    # Restore settings
    st.session_state.web_search_enabled = web_search_enabled
    st.session_state.similarity_threshold = similarity_threshold
    st.session_state.force_web_search = force_web_search
    st.session_state.llm_provider = llm_provider
    st.session_state.llm_model = llm_model

    # Add initial greeting for new conversation
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            f"สวัสดีครับ ผมคือ {FRONTEND_CONFIG['BOT_NAME']} "
            "ยินดีช่วยตอบคำถามเกี่ยวกับหลักสูตร รายวิชา อาจารย์ ระเบียบการศึกษา "
            "และข้อมูลติดต่อของภาควิชาครับ"
        )
    })
