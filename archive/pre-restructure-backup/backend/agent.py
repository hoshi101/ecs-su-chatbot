import os
from typing import List, Literal, TypedDict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

# Import API keys from config - NEW: Using Google API instead of Groq
from backend.config import (
    GOOGLE_API_KEY, TAVILY_API_KEY,
    DOMAIN_NAME, BOT_NAME, SEARCH_DOMAINS, SPECIALTY_AREAS,
    FINANCIAL_TEMPERATURE, ENABLE_QUERY_ENHANCEMENT
)
from backend.vectorstore import get_retriever

# --- Tools ---
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
# HERO Bot Domain-Restricted Web Search (Identical to Original)
tavily = TavilySearch(
    max_results=5,  # HERO Bot uses 5 results
    topic="general",
    include_domains=SEARCH_DOMAINS  # Restrict to Finansia Hero domains only
)

@tool
def web_search_tool(query: str) -> str:
    """Up-to-date web info via Tavily"""
    try:
        result = tavily.invoke({"query": query})
        if isinstance(result, dict) and 'results' in result:
            formatted_results = []
            for item in result['results']:
                title = item.get('title', 'No title')
                content = item.get('content', 'No content')
                url = item.get('url', '')
                formatted_results.append(f"Title: {title}\nContent: {content}\nURL: {url}")
            return "\n\n".join(formatted_results) if formatted_results else "No results found"
        else:
            return str(result)
    except Exception as e:
        return f"WEB_ERROR::{e}"

@tool
def rag_search_tool(query: str) -> str:
    """Top-K chunks from KB (empty string if none)"""
    try:
        retriever_instance = get_retriever()
        docs = retriever_instance.invoke(query, k=5) # Increased from 3 to 5
        return "\n\n".join(d.page_content for d in docs) if docs else ""
    except Exception as e:
        return f"RAG_ERROR::{e}"

# --- Pydantic schemas for structured output ---
class RouteDecision(BaseModel):
    route: Literal["rag", "web", "answer", "end"]
    reply: str | None = Field(None, description="Filled only when route == 'end'")

class RagJudge(BaseModel):
    sufficient: bool = Field(..., description="True if retrieved information is sufficient to answer the user's question, False otherwise.")

# --- LLM instances with structured output - NEW: Using Gemini instead of Groq ---
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Initialize Gemini models with appropriate configurations
router_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
).with_structured_output(RouteDecision)

judge_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
).with_structured_output(RagJudge)

answer_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=FINANCIAL_TEMPERATURE,  # HERO Bot uses 0.3 for financial accuracy
    google_api_key=GOOGLE_API_KEY
)

# NEW: HERO Bot Query Rewriter Agent (identical to original HERO Bot)
query_rewriter_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=FINANCIAL_TEMPERATURE,
    google_api_key=GOOGLE_API_KEY
)

# --- Shared state type ---
class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    route: Literal["rag", "web", "answer", "end"]
    rag: str
    web: str
    web_search_enabled: bool # NEW: Add web search enabled flag to state
    # NEW: HERO Bot query enhancement tracking
    original_query: str
    enhanced_query: str
    query_enhancement_enabled: bool

# --- NEW: HERO Bot Query Enhancement Function (Identical to Original) ---
def enhance_query_hero_bot_style(original_query: str) -> str:
    """
    HERO Bot Query Rewriter - Transforms vague questions into specific, searchable queries.
    Identical to the original HERO Bot's query rewriter agent.
    """
    if not ENABLE_QUERY_ENHANCEMENT:
        return original_query

    specialty_areas_text = "\n".join([f"- {area}" for area in SPECIALTY_AREAS])

    enhancement_prompt = f"""You are a {DOMAIN_NAME} support specialist expert at reformulating customer questions.
Your task is to:
1. Analyze the customer's trading platform question
2. Rewrite it to be more specific and help-desk friendly
3. Expand any trading acronyms or platform-specific terms
4. Return ONLY the rewritten query without any additional text or explanations

You specialize in:
{specialty_areas_text}

Example 1:
User: "How do I use stop loss?"
Output: "How to set up and configure stop loss orders in {DOMAIN_NAME} trading platform, including order types and risk management features"

Example 2:
User: "Chart not working"
Output: "Troubleshoot chart display issues, technical analysis tools, and charting functionality problems in {DOMAIN_NAME} platform"

Example 3:
User: "What are the platform features?"
Output: "Complete overview of {DOMAIN_NAME} trading platform features, tools, and functionality for traders"

Customer Question: {original_query}

Enhanced Query:"""

    try:
        response = query_rewriter_llm.invoke([HumanMessage(content=enhancement_prompt)])
        enhanced_query = response.content.strip()

        # Ensure we got an enhanced query (not just the original)
        if enhanced_query and enhanced_query != original_query:
            print(f"✅ Query enhanced: '{original_query}' → '{enhanced_query}'")
            return enhanced_query
        else:
            print(f"⚠️ Query enhancement returned original query: '{original_query}'")
            return original_query
    except Exception as e:
        print(f"❌ Query enhancement error: {e}")
        return original_query

# --- Node 1: router (decision) ---
def router_node(state: AgentState,config : RunnableConfig) -> AgentState:
    print("\n--- Entering router_node ---")

    # Step 1: Extract original user query
    original_query = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    print(f"Original user query: {original_query}")

    # Step 2: HERO Bot Query Enhancement (Identical to Original HERO Bot)
    enhanced_query = enhance_query_hero_bot_style(original_query)
    query = enhanced_query  # Use enhanced query for all routing decisions

    print(f"Enhanced query for routing: {query}")
    
    # Step 3: Get web search configuration
    web_search_enabled = config.get("configurable", {}).get("web_search_enabled", True)
    print(f"Web search enabled: {web_search_enabled}")

    # Step 4: HERO Bot Domain-Specific Routing Prompts (Identical to Original)
    system_prompt = f"""You are {BOT_NAME}, an intelligent routing agent for the {DOMAIN_NAME}.
Your primary goal is to direct trading platform questions to the most appropriate source for accurate financial guidance.

You specialize in:
{chr(10).join([f"- {area}" for area in SPECIALTY_AREAS])}

Prioritize using the **internal knowledge base (RAG)** for:
- Platform features and navigation guidance
- Trading procedures and order management
- Account settings and configurations
- Risk management strategies
- Troubleshooting platform issues
- Any information likely contained in trading platform documentation"""
    
    if web_search_enabled:
        system_prompt += f"""

You **CAN** use web search for queries requiring current market data, recent trading news, or information not in platform docs.
**IMPORTANT**: Web search is restricted to trusted financial sources only.

Choose one of the following routes:
- 'rag': For platform-specific questions, trading procedures, account management, or any information in {DOMAIN_NAME} documentation
- 'web': For current market conditions, recent financial news, or external trading resources (searched only on trusted financial sites)
- 'answer': For simple greetings or basic questions that don't require external lookup
- 'end': For pure small-talk where no factual answer is expected (provide a 'reply' field)"""
    else:
        system_prompt += f"""

**Web search is currently DISABLED by user preference.**
You **MUST NOT** choose the 'web' route.

Choose one of the following routes:
- 'rag': For all {DOMAIN_NAME} questions, trading queries, platform help, AND any questions that would normally go to web search
- 'answer': For simple questions answerable without external lookup
- 'end': For greetings or small-talk (provide a 'reply' field)"""

    # Add HERO Bot specific routing examples
    system_prompt += f"""

Example routing decisions for {DOMAIN_NAME}:
- User: "How do I set up stop loss orders?" -> Route: 'rag' (Platform feature, likely in documentation)
- User: "Chart is not displaying properly" -> Route: 'rag' (Platform troubleshooting)
- User: "What's the latest Bitcoin price?" -> Route: 'web' (Current market data, requires external search)
- User: "How do I reset my password?" -> Route: 'rag' (Account management procedure)
- User: "Hello there!" -> Route: 'end', reply='Hello! I'm {BOT_NAME}, your {DOMAIN_NAME} assistant. How can I help you today?'"""

    messages = [
        ("system", system_prompt),
        ("user", query)
    ]
    
    result: RouteDecision = router_llm.invoke(messages)
    
    initial_router_decision = result.route # Store the LLM's raw decision
    router_override_reason = None

    # NEW LOGIC: Override router decision if web search is disabled and LLM chose 'web'
    if not web_search_enabled and result.route == "web":
        # If web search is disabled, force it to try RAG instead
        result.route = "rag" 
        router_override_reason = "Web search disabled by user; redirected to RAG."
        print(f"Router decision overridden: changed from 'web' to 'rag' because web search is disabled.")
    
    print(f"Router final decision: {result.route}, Reply (if 'end'): {result.reply}")

    # Step 5: Build output state with HERO Bot query enhancement tracking
    out = {
        "messages": state["messages"],
        "route": result.route,
        "web_search_enabled": web_search_enabled,
        # NEW: Track HERO Bot query enhancement for UI display
        "original_query": original_query,
        "enhanced_query": enhanced_query,
        "query_enhancement_enabled": ENABLE_QUERY_ENHANCEMENT
    }

    if router_override_reason: # Add override info for tracing
        out["initial_router_decision"] = initial_router_decision
        out["router_override_reason"] = router_override_reason

    if result.route == "end":
        # Use HERO Bot's greeting style
        default_reply = f"Hello! I'm {BOT_NAME}, your {DOMAIN_NAME} assistant. How can I help you today?"
        out["messages"] = state["messages"] + [AIMessage(content=result.reply or default_reply)]

    print("--- Exiting router_node ---")
    return out

# --- Node 2: RAG lookup ---
def rag_node(state: AgentState,config:RunnableConfig) -> AgentState:
    print("\n--- Entering rag_node ---")

    # Step 1: Use enhanced query from HERO Bot query rewriter
    enhanced_query = state.get("enhanced_query", "")
    original_query = state.get("original_query", "")
    query = enhanced_query if enhanced_query else original_query

    print(f"RAG using enhanced query: {query}")

    # Step 2: Get configuration
    web_search_enabled = config.get("configurable", {}).get("web_search_enabled", True)
    print(f"Web search enabled: {web_search_enabled}")

    # Step 3: Retrieve documents using enhanced query
    chunks = rag_search_tool.invoke(query)
    
    if chunks.startswith("RAG_ERROR::"):
        print(f"RAG Error: {chunks}. Checking web search enabled status.")
        # If RAG fails, and web search is enabled, try web. Otherwise, go to answer.
        next_route = "web" if web_search_enabled else "answer"
        return {**state, "rag": "", "route": next_route}

    if chunks:
        print(f"Retrieved RAG chunks (first 500 chars): {chunks[:500]}...")
    else:
        print("No RAG chunks retrieved.")

    # Step 4: HERO Bot Specialized RAG Judge (Trading Platform Focus)
    judge_messages = [
        ("system", f"""You are a {DOMAIN_NAME} specialist evaluating if retrieved information is sufficient for trading platform questions.

You specialize in:
{chr(10).join([f"- {area}" for area in SPECIALTY_AREAS])}

Evaluate if the retrieved information can fully answer the trading platform question:
- **SUFFICIENT**: Information directly explains platform features, procedures, or solutions
- **NOT SUFFICIENT**: Information is vague, incomplete, outdated, or doesn't address the specific trading platform question

For {DOMAIN_NAME} questions, prioritize:
- Step-by-step trading procedures
- Platform feature explanations
- Account management guidance
- Risk management strategies
- Troubleshooting solutions

If no relevant platform information was retrieved, it is NOT sufficient.

Examples for {DOMAIN_NAME}:
- Question: "How to set stop loss?" Retrieved: "Stop loss orders can be configured in the order panel..." -> {{"sufficient": true}}
- Question: "Chart not loading?" Retrieved: "Charts may have display issues..." -> {{"sufficient": true}}
- Question: "How to deposit funds?" Retrieved: "General banking information..." -> {{"sufficient": false}} (Not platform-specific)

Respond ONLY with JSON: {{"sufficient": true/false}}"""),
        ("user", f"Trading Platform Question: {original_query}\nEnhanced Query: {query}\n\nRetrieved Platform Info: {chunks}\n\nIs this sufficient to answer the {DOMAIN_NAME} question?")
    ]
    verdict: RagJudge = judge_llm.invoke(judge_messages)
    print(f"RAG Judge verdict: {verdict.sufficient}")
    print("--- Exiting rag_node ---")
    
    # NEW LOGIC: Decide next route based on sufficiency AND web_search_enabled
    if verdict.sufficient:
        next_route = "answer"
    else:
        next_route = "web" if web_search_enabled else "answer" # If not sufficient, only go to web if enabled
        print(f"RAG not sufficient. Web search enabled: {web_search_enabled}. Next route: {next_route}")

    return {
        **state,
        "rag": chunks,
        "route": next_route,
        "web_search_enabled": web_search_enabled,
        # Preserve HERO Bot query enhancement information
        "original_query": original_query,
        "enhanced_query": enhanced_query,
        "query_enhancement_enabled": state.get("query_enhancement_enabled", ENABLE_QUERY_ENHANCEMENT)
    }

# --- Node 3: web search ---
def web_node(state: AgentState,config:RunnableConfig) -> AgentState:
    print("\n--- Entering web_node ---")

    # Step 1: Use enhanced query from HERO Bot query rewriter
    enhanced_query = state.get("enhanced_query", "")
    original_query = state.get("original_query", "")
    query = enhanced_query if enhanced_query else original_query

    print(f"Web search using enhanced query: {query}")

    # Step 2: Check if web search is enabled
    web_search_enabled = config.get("configurable", {}).get("web_search_enabled", True)
    print(f"Web search enabled: {web_search_enabled}")

    if not web_search_enabled:
        print("Web search disabled by user. Skipping search.")
        return {
            **state,
            "web": f"Web search was disabled by the user for {DOMAIN_NAME} queries.",
            "route": "answer"
        }

    # Step 3: Perform HERO Bot domain-restricted web search
    print(f"Searching {SEARCH_DOMAINS} for: {query}")
    snippets = web_search_tool.invoke(query)
    
    if snippets.startswith("WEB_ERROR::"):
        print(f"Web Error: {snippets}. Proceeding to answer with limited info.")
        return {**state, "web": "", "route": "answer"}

    print(f"Web snippets retrieved from {SEARCH_DOMAINS}: {snippets[:200]}...")
    print("--- Exiting web_node ---")
    return {
        **state,
        "web": snippets,
        "route": "answer",
        # Preserve HERO Bot query enhancement information
        "original_query": original_query,
        "enhanced_query": enhanced_query
    }

# --- Node 4: final answer ---
def answer_node(state: AgentState) -> AgentState:
    print("\n--- Entering answer_node ---")

    # Step 1: Get queries (original and enhanced)
    original_query = state.get("original_query", "")
    enhanced_query = state.get("enhanced_query", "")
    user_q = original_query if original_query else next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")

    print(f"Generating answer for: {user_q}")
    if enhanced_query and enhanced_query != original_query:
        print(f"Using enhanced context: {enhanced_query}")

    # Step 2: Process context with HERO Bot's specialized approach
    ctx_parts = []
    source_info = []

    if state.get("rag"):
        ctx_parts.append(f"Platform Documentation:\n{state['rag']}")
        source_info.append("internal platform documentation")

    if state.get("web"):
        # Only include actual web search results (not disabled messages)
        web_content = state["web"]
        if web_content and not web_content.startswith(f"Web search was disabled"):
            ctx_parts.append(f"External Trading Resources:\n{web_content}")
            source_info.append(f"external resources from {', '.join(SEARCH_DOMAINS)}")

    context = "\n\n".join(ctx_parts)
    source_description = " and ".join(source_info) if source_info else "general knowledge"

    # Step 3: HERO Bot Specialized Response Generation (Identical to Original)
    specialty_areas_text = "\n".join([f"- {area}" for area in SPECIALTY_AREAS])

    if context.strip():
        prompt = f"""You are {BOT_NAME}, the expert trading platform assistant for {DOMAIN_NAME}.

Your specialization areas:
{specialty_areas_text}

IMPORTANT GUIDELINES:
- Prioritize official {DOMAIN_NAME} platform information when available
- Provide step-by-step guidance when possible
- Reference specific platform features and menu locations
- Maintain a helpful, professional tone for financial guidance
- When using external sources, clearly indicate they come from external resources
- Focus on practical application for {DOMAIN_NAME} users

Customer Question: {user_q}
Enhanced Context Query: {enhanced_query}

Available Information:
{context}

Instructions: Provide helpful, actionable guidance for this {DOMAIN_NAME} user based on the {source_description}."""

    else:
        prompt = f"""You are {BOT_NAME}, the expert trading platform assistant for {DOMAIN_NAME}.

Your specialization areas:
{specialty_areas_text}

Customer Question: {user_q}
Enhanced Query: {enhanced_query}

No specific platform documentation or external trading resources were found for this query.

Instructions: Provide the best possible guidance based on your knowledge of trading platforms and financial systems. Acknowledge the limitation and suggest how the user might find more specific information if needed."""

    print(f"HERO Bot prompt (first 300 chars): {prompt[:300]}...")
    ans = answer_llm.invoke([HumanMessage(content=prompt)]).content
    print(f"HERO Bot response generated: {ans[:200]}...")
    print("--- Exiting answer_node ---")

    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=ans)]
    }

# --- Routing helpers ---
def from_router(st: AgentState) -> Literal["rag", "web", "answer", "end"]:
    return st["route"]

def after_rag(st: AgentState) -> Literal["answer", "web"]:
    return st["route"]

def after_web(_) -> Literal["answer"]:
    return "answer"

# --- Build graph ---
def build_agent():
    """Builds and compiles the LangGraph agent."""
    g = StateGraph(AgentState)
    g.add_node("router", router_node)
    g.add_node("rag_lookup", rag_node)
    g.add_node("web_search", web_node)
    g.add_node("answer", answer_node)

    g.set_entry_point("router")
    
    g.add_conditional_edges(
        "router",
        from_router,
        {
            "rag": "rag_lookup",
            "web": "web_search",
            "answer": "answer",
            "end": END
        }
    )
    
    g.add_conditional_edges(
        "rag_lookup",
        after_rag,
        {
            "answer": "answer",
            "web": "web_search"
        }
    )
    
    g.add_edge("web_search", "answer")
    g.add_edge("answer", END)

    agent = g.compile(checkpointer=MemorySaver())
    return agent

rag_agent = build_agent()