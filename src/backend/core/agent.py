import os
import re
from typing import Any, Dict, List, Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from src.backend.core.config import (
    BOT_NAME,
    DEFAULT_LANGUAGE,
    DOMAIN_NAME,
    ENABLE_QUERY_ENHANCEMENT,
    FACULTY_CONTACT_TEXT,
    FINANCIAL_TEMPERATURE,
    GOOGLE_API_KEY,
    OPENAI_API_KEY,
    PROVIDER_MODEL_SUGGESTIONS,
    SEARCH_DOMAINS,
    SENSITIVE_TOPIC_POLICY,
    SPECIALTY_AREAS,
    TAVILY_API_KEY,
    normalize_provider,
    resolve_model_name,
)
from src.backend.services.vectorstore import retrieve_documents
from src.backend.utils.logging_utils import get_logger

logger = get_logger(__name__)


os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY or ""
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY or ""

tavily = TavilySearch(
    max_results=5,
    topic="general",
    include_domains=SEARCH_DOMAINS,
)


class RouteDecision(BaseModel):
    route: Literal["rag", "web", "answer", "end"]
    reply: str | None = Field(None, description="Filled only when route == 'end'")


class RagJudge(BaseModel):
    sufficient: bool = Field(..., description="Whether the retrieved content is sufficient to answer the question.")


class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    route: Literal["rag", "web", "answer", "end"]
    rag: str
    web: str
    rag_documents: List[Dict[str, Any]]
    web_results: List[Dict[str, Any]]
    web_search_enabled: bool
    original_query: str
    enhanced_query: str
    query_enhancement_enabled: bool
    force_web_search: bool
    similarity_threshold: float
    initial_router_decision: str
    router_override_reason: str
    llm_provider: str
    llm_model: str
    rag_status: Literal["sufficient", "insufficient", "empty", "error"]
    rag_error: str
    query_enhancement_status: Literal["enhanced", "skipped", "unchanged"]
    query_enhancement_reason: str
    precheck_intent: Literal["contact", "greeting", "out_of_scope", "domain_question"]
    precheck_reason: str


def get_available_model_suggestions() -> Dict[str, List[str]]:
    return PROVIDER_MODEL_SUGGESTIONS


def get_default_llm_settings() -> Dict[str, str]:
    provider = normalize_provider(None)
    return {
        "provider": provider,
        "model": resolve_model_name(provider),
    }


def resolve_runtime_llm_settings(
    provider: str | None = None,
    model_name: str | None = None,
) -> Dict[str, str]:
    provider_name = normalize_provider(provider)
    resolved_model = resolve_model_name(provider_name, model_name)
    return {
        "provider": provider_name,
        "model": resolved_model,
    }


def build_chat_model(
    provider: str | None = None,
    model_name: str | None = None,
    *,
    temperature: float = 0,
) -> BaseChatModel:
    settings = resolve_runtime_llm_settings(provider, model_name)
    provider_name = settings["provider"]
    resolved_model = settings["model"]

    if provider_name == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured.")
        return ChatOpenAI(
            model=resolved_model,
            temperature=temperature,
            api_key=OPENAI_API_KEY,
        )

    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not configured.")
    return ChatGoogleGenerativeAI(
        model=resolved_model,
        temperature=temperature,
        google_api_key=GOOGLE_API_KEY,
    )


def get_runtime_settings_from_state(state: AgentState) -> Dict[str, str]:
    return resolve_runtime_llm_settings(
        state.get("llm_provider"),
        state.get("llm_model"),
    )


def build_default_greeting() -> str:
    if DEFAULT_LANGUAGE.lower().startswith("th"):
        return (
            f"สวัสดีครับ ผมคือ {BOT_NAME} ผู้ช่วยข้อมูลของ{DOMAIN_NAME} "
            "ผมช่วยตอบคำถามเกี่ยวกับหลักสูตร รายวิชา อาจารย์ ระเบียบการศึกษา และข้อมูลติดต่อภาควิชาได้ครับ"
        )
    return (
        f"Hello, I'm {BOT_NAME}, the information assistant for {DOMAIN_NAME}. "
        "I can help with curriculum, courses, lecturers, regulations, and department contact information."
    )


def build_query_enhancement_prompt(original_query: str) -> str:
    specialty_areas_text = "\n".join(f"- {area}" for area in SPECIALTY_AREAS)
    return f"""You are a query rewriting assistant for {DOMAIN_NAME}.

Your job:
1. Rewrite the user's question so it is easier to search in a university department knowledge base.
2. Keep the meaning intact.
3. Expand short or vague wording when useful.
4. Preserve the original language unless clarification requires a bilingual hint.
5. Return ONLY the rewritten query.

The knowledge base focuses on:
{specialty_areas_text}

Examples:
- User: "อาจารย์โสภณทำวิจัยอะไร" -> "ข้อมูลอาจารย์โสภณ ผู้มีจรรยา งานวิจัย ความเชี่ยวชาญ และประวัติการศึกษา"
- User: "prerequisite ของสาขามีไหม" -> "หลักสูตรสาขาวิศวกรรมอิเล็กทรอนิกส์และระบบคอมพิวเตอร์ รายวิชาบังคับก่อน prerequisite และแผนการเรียน"
- User: "How can I contact the department?" -> "Department of Electrical Engineering contact information phone email office address Facebook"

User question: {original_query}

Rewritten query:"""


NON_INFORMATIONAL_PATTERNS = (
    r"^(hi|hello|hey|yo|ok|okay|thanks|thank you|thx|sure|yes|no|lol|555+|ครับ|ค่ะ|คับ|จ้า|โอเค|ได้เลย|ขอบคุณ|หวัดดี|สวัสดี)$",
    r"^(กินข้าวยัง|ไปไหนมา|เป็นไงบ้าง|สบายดีไหม|ทำอะไรอยู่)$",
)

DOMAIN_HINTS = (
    "ภาควิชา",
    "สาขา",
    "มหาลัย",
    "มหาวิทยาลัย",
    "คณะ",
    "หลักสูตร",
    "รายวิชา",
    "อาจารย์",
    "บุคลากร",
    "ติดต่อ",
    "โทร",
    "facebook",
    "website",
    "contact",
    "course",
    "curriculum",
    "lecturer",
    "department",
    "internship",
    "co-op",
    "coop",
    "prerequisite",
)

CONTACT_HINTS = (
    "ติดต่อ",
    "contact",
    "โทร",
    "phone",
    "เบอร์",
    "facebook",
    "email",
    "อีเมล",
    "ที่อยู่",
    "address",
    "website",
    "เว็บ",
    "location",
    "สถานที่ตั้ง",
)

GREETING_PATTERNS = (
    r"^(hi|hello|hey|yo|สวัสดี|หวัดดี)$",
    r"^(hi|hello|hey|yo|สวัสดี|หวัดดี)\s+(ครับ|ค่ะ|คับ|จ้า)?$",
)

OUT_OF_SCOPE_PATTERNS = (
    r"^(กินข้าวยัง|กินไรดี|ไปไหนมา|เป็นไงบ้าง|สบายดีไหม|ทำอะไรอยู่)$",
    r"^(เล่าเรื่องตลก|ดูดวง|แต่งเพลง|เขียนโค้ด|คำนวณหวย|แนะนำหนัง|สรุปข่าว)$",
)


def should_enhance_query(original_query: str) -> tuple[bool, str]:
    query = " ".join(original_query.strip().split())
    normalized = query.lower().strip(" \t\n\r?!.,")

    if not ENABLE_QUERY_ENHANCEMENT:
        return False, "Query enhancement is disabled."
    if not query:
        return False, "Empty query."

    for pattern in NON_INFORMATIONAL_PATTERNS:
        if re.fullmatch(pattern, normalized):
            return False, "Small talk or acknowledgement does not need search enhancement."

    token_count = len(query.split())
    has_domain_hint = any(term in normalized for term in DOMAIN_HINTS)

    if not has_domain_hint and token_count <= 5:
        return False, "Short non-domain query does not need enhancement."

    if has_domain_hint and (len(query) >= 60 or token_count >= 8):
        return False, "Query is already specific enough for retrieval."

    return True, "Query may benefit from retrieval-oriented rewriting."


def build_contact_response() -> str:
    return f"""ได้เลยครับ นี่คือข้อมูลติดต่อของ{DOMAIN_NAME}

- โทรศัพท์: 034-219364-66 ต่อ 25520
- มือถือ: 089-979-7911
- โทรศัพท์/โทรสาร: 034-241971
- Facebook: Department of Electrical Engineering - Silpakorn University

หากต้องการ ผมช่วยสรุปเป็นรูปแบบสั้นสำหรับส่งต่อได้ครับ"""


def build_out_of_scope_response() -> str:
    return f"""ขออภัยครับ ผมช่วยได้เฉพาะข้อมูลที่เกี่ยวข้องกับ{DOMAIN_NAME} เช่น

- หลักสูตรและรายวิชา
- อาจารย์และบุคลากร
- ระเบียบและเอกสาร
- ข้อมูลติดต่อภาควิชา

ถ้าคุณมีคำถามเกี่ยวกับภาควิชาหรือมหาวิทยาลัยในส่วนนี้ ส่งมาได้เลยครับ"""


def normalize_for_rules(text: str) -> str:
    return " ".join(text.strip().lower().split()).strip(" \t\n\r?!.,")


def classify_query_precheck(original_query: str) -> tuple[Literal["contact", "greeting", "out_of_scope", "domain_question"], str]:
    normalized = normalize_for_rules(original_query)
    if not normalized:
        return "greeting", "Empty input treated as a greeting/help prompt."

    has_domain_hint = any(term in normalized for term in DOMAIN_HINTS)
    has_contact_hint = any(term in normalized for term in CONTACT_HINTS)

    for pattern in GREETING_PATTERNS:
        if re.fullmatch(pattern, normalized):
            return "greeting", "Greeting matched a direct template response."

    if has_domain_hint and has_contact_hint:
        return "contact", "Contact keywords matched a direct template response."

    for pattern in OUT_OF_SCOPE_PATTERNS:
        if re.fullmatch(pattern, normalized):
            return "out_of_scope", "Clearly outside the chatbot scope."

    if not has_domain_hint and len(normalized.split()) <= 6:
        return "out_of_scope", "Short query without department or university hints."

    return "domain_question", "Query appears related to the department knowledge domain."


def enhance_query_hero_bot_style(original_query: str) -> str:
    return enhance_query_with_provider(original_query, None, None)


def enhance_query_with_provider(
    original_query: str,
    provider: str | None,
    model_name: str | None,
) -> str:
    if not ENABLE_QUERY_ENHANCEMENT or not original_query.strip():
        return original_query

    try:
        query_rewriter_llm = build_chat_model(
            provider,
            model_name,
            temperature=0.1,
        )
        response = query_rewriter_llm.invoke(
            [HumanMessage(content=build_query_enhancement_prompt(original_query))]
        )
        enhanced_query = response.content.strip()
        if enhanced_query:
            return enhanced_query
    except Exception as exc:
        logger.warning("Query enhancement error | error=%s", exc)

    return original_query


@tool
def web_search_tool(query: str) -> str:
    """Search official department/faculty sources for up-to-date public information."""
    try:
        result = tavily.invoke({"query": query})
        if isinstance(result, dict) and "results" in result:
            formatted_results = []
            for item in result["results"]:
                title = item.get("title", "No title")
                content = item.get("content", "No content")
                url = item.get("url", "")
                formatted_results.append(f"Title: {title}\nContent: {content}\nURL: {url}")
            return "\n\n".join(formatted_results) if formatted_results else ""
        return str(result)
    except Exception as exc:
        return f"WEB_ERROR::{exc}"


def get_query_context(state: AgentState) -> tuple[str, str]:
    original_query = state.get("original_query") or next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        "",
    )
    enhanced_query = state.get("enhanced_query") or original_query
    return original_query, enhanced_query


def router_node(state: AgentState) -> AgentState:
    original_query, enhanced_query = get_query_context(state)
    runtime_settings = get_runtime_settings_from_state(state)
    precheck_intent, precheck_reason = classify_query_precheck(original_query)

    base_state: AgentState = {
        "messages": state["messages"],
        "web_search_enabled": state.get("web_search_enabled", True),
        "force_web_search": state.get("force_web_search", False),
        "similarity_threshold": state.get("similarity_threshold", 0.7),
        "original_query": original_query,
        "enhanced_query": original_query,
        "query_enhancement_enabled": ENABLE_QUERY_ENHANCEMENT,
        "llm_provider": runtime_settings["provider"],
        "llm_model": runtime_settings["model"],
        "query_enhancement_status": "skipped",
        "query_enhancement_reason": "Template or shortcut response does not need query rewriting.",
        "precheck_intent": precheck_intent,
        "precheck_reason": precheck_reason,
    }

    if precheck_intent == "contact":
        return {
            **base_state,
            "route": "end",
            "messages": state["messages"] + [AIMessage(content=build_contact_response())],
        }

    if precheck_intent == "greeting":
        return {
            **base_state,
            "route": "end",
            "messages": state["messages"] + [AIMessage(content=build_default_greeting())],
        }

    if precheck_intent == "out_of_scope":
        return {
            **base_state,
            "route": "end",
            "messages": state["messages"] + [AIMessage(content=build_out_of_scope_response())],
        }

    should_enhance, enhancement_reason = should_enhance_query(original_query)
    enhancement_status: Literal["enhanced", "skipped", "unchanged"] = "skipped"
    if should_enhance:
        enhanced_query = enhance_query_with_provider(
            original_query,
            runtime_settings["provider"],
            runtime_settings["model"],
        )
        enhancement_status = "enhanced" if enhanced_query != original_query else "unchanged"
        if enhancement_status == "unchanged":
            enhancement_reason = "The original wording was already suitable for retrieval."
    else:
        enhanced_query = original_query
    query = enhanced_query or original_query

    web_search_enabled = state.get("web_search_enabled", True)
    force_web_search = state.get("force_web_search", False)

    system_prompt = f"""You are {BOT_NAME}, a routing assistant for {DOMAIN_NAME}.

Your supported scope:
{chr(10).join(f"- {area}" for area in SPECIALTY_AREAS)}

Routing policy:
- Use 'rag' for department questions about curriculum, courses, lecturers, regulations, internships, forms, services, or official contact information.
- Use 'web' only when the question may require newer public information from official department/faculty websites and web search is allowed.
- Use 'answer' for simple greetings or straightforward policy answers that need no retrieval.
- Use 'end' only for pure small talk.

Safety policy:
- Refuse to guess.
- Do not answer sensitive personal questions unless clearly supported by official public sources.
- {SENSITIVE_TOPIC_POLICY}
"""

    if web_search_enabled:
        system_prompt += (
            f"\nWeb search is available only for these domains: {', '.join(SEARCH_DOMAINS)}."
        )
    else:
        system_prompt += "\nWeb search is disabled. Do not route to 'web'."

    messages = [("system", system_prompt), ("user", query)]
    router_llm = build_chat_model(
        runtime_settings["provider"],
        runtime_settings["model"],
        temperature=0,
    ).with_structured_output(RouteDecision)
    result: RouteDecision = router_llm.invoke(messages)

    initial_route = result.route
    override_reason = ""

    if force_web_search and web_search_enabled and result.route in {"rag", "answer"}:
        result.route = "web"
        override_reason = "User forced web search."
    elif not web_search_enabled and result.route == "web":
        result.route = "rag"
        override_reason = "Web search disabled by user."

    out: AgentState = {
        "messages": state["messages"],
        "route": result.route,
        "web_search_enabled": web_search_enabled,
        "force_web_search": force_web_search,
        "similarity_threshold": state.get("similarity_threshold", 0.7),
        "original_query": original_query,
        "enhanced_query": enhanced_query,
        "query_enhancement_enabled": ENABLE_QUERY_ENHANCEMENT,
        "llm_provider": runtime_settings["provider"],
        "llm_model": runtime_settings["model"],
        "query_enhancement_status": enhancement_status,
        "query_enhancement_reason": enhancement_reason,
        "precheck_intent": precheck_intent,
        "precheck_reason": precheck_reason,
    }

    if result.route == "end":
        out["messages"] = state["messages"] + [AIMessage(content=result.reply or build_default_greeting())]

    if override_reason:
        out["initial_router_decision"] = initial_route
        out["router_override_reason"] = override_reason

    return out


def format_rag_context(documents: List[Dict[str, Any]]) -> str:
    formatted_chunks = []
    for index, item in enumerate(documents, start=1):
        metadata = item.get("metadata", {})
        label = metadata.get("file_name") or metadata.get("title") or metadata.get("source") or "Document"
        formatted_chunks.append(
            f"[Source {index}: {label}]\n{item.get('content', '')}"
        )
    return "\n\n".join(formatted_chunks)


def rag_node(state: AgentState) -> AgentState:
    original_query, enhanced_query = get_query_context(state)
    similarity_threshold = state.get("similarity_threshold", 0.7)
    runtime_settings = get_runtime_settings_from_state(state)
    query = enhanced_query or original_query

    try:
        documents = retrieve_documents(
            query,
            top_k=5,
            similarity_threshold=similarity_threshold,
        )
    except Exception as exc:
        logger.exception("RAG retrieval error | query=%s", query)
        next_route = "web" if state.get("web_search_enabled", True) else "answer"
        return {
            **state,
            "rag": "",
            "rag_documents": [],
            "route": next_route,
            "rag_status": "error",
            "rag_error": str(exc),
            "llm_provider": runtime_settings["provider"],
            "llm_model": runtime_settings["model"],
        }

    rag_text = format_rag_context(documents)
    if not rag_text.strip():
        next_route = "web" if state.get("web_search_enabled", True) else "answer"
        return {
            **state,
            "rag": "",
            "rag_documents": [],
            "route": next_route,
            "rag_status": "empty",
            "llm_provider": runtime_settings["provider"],
            "llm_model": runtime_settings["model"],
        }

    judge_prompt = f"""You are evaluating whether retrieved department information is sufficient to answer the user's question.

Question: {original_query}
Enhanced query: {query}

Retrieved information:
{rag_text}

Return sufficient=true only if the retrieved content is enough to answer accurately without guessing.
If the content is incomplete, unrelated, or too weak, return sufficient=false.
"""

    judge_llm = build_chat_model(
        runtime_settings["provider"],
        runtime_settings["model"],
        temperature=0,
    ).with_structured_output(RagJudge)
    verdict: RagJudge = judge_llm.invoke([HumanMessage(content=judge_prompt)])
    next_route = "answer" if verdict.sufficient else ("web" if state.get("web_search_enabled", True) else "answer")

    return {
        **state,
        "rag": rag_text,
        "rag_documents": documents,
        "route": next_route,
        "original_query": original_query,
        "enhanced_query": enhanced_query,
        "llm_provider": runtime_settings["provider"],
        "llm_model": runtime_settings["model"],
        "rag_status": "sufficient" if verdict.sufficient else "insufficient",
    }


def web_node(state: AgentState) -> AgentState:
    original_query, enhanced_query = get_query_context(state)
    runtime_settings = get_runtime_settings_from_state(state)
    query = enhanced_query or original_query

    if not state.get("web_search_enabled", True):
        return {**state, "web": "", "web_results": [], "route": "answer"}

    snippets = web_search_tool.invoke(query)
    if snippets.startswith("WEB_ERROR::"):
        logger.warning("Web search error | query=%s | details=%s", query, snippets)
        return {**state, "web": "", "web_results": [], "route": "answer"}

    web_results = []
    for block in [block.strip() for block in snippets.split("\n\n") if block.strip()]:
        title = ""
        content = ""
        url = ""
        for line in block.splitlines():
            if line.startswith("Title: "):
                title = line.replace("Title: ", "", 1).strip()
            elif line.startswith("Content: "):
                content = line.replace("Content: ", "", 1).strip()
            elif line.startswith("URL: "):
                url = line.replace("URL: ", "", 1).strip()
        web_results.append({"title": title, "snippet": content, "url": url})

    return {
        **state,
        "web": snippets,
        "web_results": web_results,
        "route": "answer",
        "original_query": original_query,
        "enhanced_query": enhanced_query,
        "llm_provider": runtime_settings["provider"],
        "llm_model": runtime_settings["model"],
    }


def build_answer_prompt(state: AgentState) -> str:
    original_query, enhanced_query = get_query_context(state)

    context_parts: List[str] = []
    if state.get("rag"):
        context_parts.append(f"Internal knowledge base:\n{state['rag']}")
    if state.get("web"):
        context_parts.append(f"Official website search results:\n{state['web']}")

    context = "\n\n".join(context_parts).strip()

    response_language = "Thai by default, but respond in English if the user asks in English."
    prompt = f"""You are {BOT_NAME}, an information assistant for {DOMAIN_NAME}.

Use this policy:
- Answer based on official department/faculty information in the provided context.
- {response_language}
- Keep the tone friendly, clear, and similar to a helpful department staff member.
- Prefer bullet points or short sections when it improves readability.
- If the answer is uncertain or missing from the context, say so clearly.
- Do not invent facts.
- Do not provide sensitive personal information beyond official public data.
- When helpful, suggest the user contact the department.
- Contact information to mention when escalation is needed: {FACULTY_CONTACT_TEXT}

Question: {original_query}
Enhanced query: {enhanced_query}

Context:
{context if context else 'No verified context found.'}

If context is available:
- Ground the answer in that context.
- Mention the source document or page briefly when helpful.

If context is not available:
- Say that the information was not found in the available official sources.
- Suggest contacting the department instead of guessing.
"""
    return prompt


def answer_node(state: AgentState) -> AgentState:
    runtime_settings = get_runtime_settings_from_state(state)
    prompt = build_answer_prompt(state)
    answer_llm = build_chat_model(
        runtime_settings["provider"],
        runtime_settings["model"],
        temperature=FINANCIAL_TEMPERATURE,
    )
    answer = answer_llm.invoke([HumanMessage(content=prompt)]).content
    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=answer)],
        "llm_provider": runtime_settings["provider"],
        "llm_model": runtime_settings["model"],
    }


def from_router(st: AgentState) -> Literal["rag", "web", "answer", "end"]:
    return st["route"]


def after_rag(st: AgentState) -> Literal["answer", "web"]:
    return st["route"]


def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("rag_lookup", rag_node)
    graph.add_node("web_search", web_node)
    graph.add_node("answer", answer_node)

    graph.set_entry_point("router")
    graph.add_conditional_edges(
        "router",
        from_router,
        {
            "rag": "rag_lookup",
            "web": "web_search",
            "answer": "answer",
            "end": END,
        },
    )
    graph.add_conditional_edges(
        "rag_lookup",
        after_rag,
        {
            "answer": "answer",
            "web": "web_search",
        },
    )
    graph.add_edge("web_search", "answer")
    graph.add_edge("answer", END)
    return graph.compile(checkpointer=MemorySaver())


rag_agent = build_agent()
