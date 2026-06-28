import json
import os
from datetime import datetime, timezone
from typing import Any, Iterable

from src.backend.utils.logging_utils import LOG_DIR, get_logger


logger = get_logger(__name__)

USAGE_LOG_FILE = os.getenv("USAGE_LOG_FILE", os.path.join(LOG_DIR, "usage_events.jsonl"))
USAGE_TRACKING_ENABLED = os.getenv("USAGE_TRACKING_ENABLED", "true").lower() not in {
    "0",
    "false",
    "no",
}
MAX_QUERY_PREVIEW_CHARS = int(os.getenv("USAGE_QUERY_PREVIEW_CHARS", "160"))


def compact_text(value: str, limit: int = MAX_QUERY_PREVIEW_CHARS) -> str:
    text = " ".join((value or "").split())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _event_details(event: Any) -> dict[str, Any]:
    if isinstance(event, dict):
        details = event.get("details", {})
    else:
        details = getattr(event, "details", {})
    return details if isinstance(details, dict) else {}


def _event_node_name(event: Any) -> str | None:
    if isinstance(event, dict):
        return event.get("node_name")
    return getattr(event, "node_name", None)


def _first_routing_details(trace_events: Iterable[Any]) -> dict[str, Any]:
    for event in trace_events or []:
        details = _event_details(event)
        if details.get("precheck_intent") or details.get("decision") or details.get("final_decision"):
            return details
    return {}


def _source_types(sources: Iterable[dict[str, Any]]) -> list[str]:
    types = {
        source.get("source_type")
        for source in sources or []
        if isinstance(source, dict) and source.get("source_type")
    }
    return sorted(types)


def build_chat_usage_event(
    *,
    session_id: str,
    query: str,
    llm_provider: str | None,
    llm_model: str | None,
    enable_web_search: bool,
    force_web_search: bool,
    similarity_threshold: float,
    trace_events: list[Any],
    sources: list[dict[str, Any]],
    latency_ms: float,
    status: str,
    error: str | None = None,
) -> dict[str, Any]:
    routing_details = _first_routing_details(trace_events)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "chat_request",
        "status": status,
        "session_id": session_id,
        "query_preview": compact_text(query),
        "query_length": len(query or ""),
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "enable_web_search": enable_web_search,
        "force_web_search": force_web_search,
        "similarity_threshold": similarity_threshold,
        "route": routing_details.get("final_decision") or routing_details.get("decision"),
        "initial_route": routing_details.get("initial_decision"),
        "precheck_intent": routing_details.get("precheck_intent"),
        "shortcut_variant": routing_details.get("shortcut_variant"),
        "query_enhanced": bool(routing_details.get("query_enhanced")),
        "latency_ms": round(latency_ms, 2),
        "trace_step_count": len(trace_events or []),
        "trace_nodes": [
            node_name
            for node_name in (_event_node_name(event) for event in trace_events or [])
            if node_name
        ],
        "source_count": len(sources or []),
        "source_types": _source_types(sources),
    }

    if error:
        event["error"] = compact_text(error, limit=240)

    return event


def write_usage_event(event: dict[str, Any]) -> None:
    if not USAGE_TRACKING_ENABLED:
        return

    try:
        os.makedirs(os.path.dirname(USAGE_LOG_FILE), exist_ok=True)
        with open(USAGE_LOG_FILE, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    except Exception as exc:
        logger.warning("Usage tracking write failed | error=%s", exc)


def record_chat_usage(**kwargs: Any) -> None:
    write_usage_event(build_chat_usage_event(**kwargs))
