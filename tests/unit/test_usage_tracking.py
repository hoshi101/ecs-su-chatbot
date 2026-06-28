import json

from src.backend.utils.usage_tracking import build_chat_usage_event, compact_text, write_usage_event


def test_build_chat_usage_event_extracts_routing_and_sources():
    event = build_chat_usage_event(
        session_id="demo-session",
        query="หลักสูตร ECS ปี 2565 รวมกี่หน่วยกิต",
        llm_provider="openai",
        llm_model="gpt-5.4-mini",
        enable_web_search=True,
        force_web_search=False,
        similarity_threshold=0.7,
        trace_events=[
            {
                "node_name": "router",
                "details": {
                    "decision": "rag",
                    "precheck_intent": "domain_question",
                    "query_enhanced": True,
                },
            },
            {"node_name": "rag_lookup", "details": {}},
            {"node_name": "answer", "details": {}},
        ],
        sources=[
            {"source_type": "Department Knowledge Base"},
            {"source_type": "Department Knowledge Base"},
        ],
        latency_ms=1234.567,
        status="success",
    )

    assert event["event_type"] == "chat_request"
    assert event["status"] == "success"
    assert event["route"] == "rag"
    assert event["precheck_intent"] == "domain_question"
    assert event["query_enhanced"] is True
    assert event["source_count"] == 2
    assert event["source_types"] == ["Department Knowledge Base"]
    assert event["latency_ms"] == 1234.57
    assert event["trace_nodes"] == ["router", "rag_lookup", "answer"]


def test_compact_text_truncates_and_normalizes_whitespace():
    assert compact_text("  hello\n\nworld  ", limit=20) == "hello world"
    assert compact_text("x" * 12, limit=10) == "xxxxxxxxxx..."


def test_write_usage_event_writes_jsonl(tmp_path, monkeypatch):
    usage_file = tmp_path / "usage_events.jsonl"
    monkeypatch.setattr("src.backend.utils.usage_tracking.USAGE_LOG_FILE", str(usage_file))
    monkeypatch.setattr("src.backend.utils.usage_tracking.USAGE_TRACKING_ENABLED", True)

    write_usage_event({"event_type": "chat_request", "status": "success"})

    lines = usage_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == {"event_type": "chat_request", "status": "success"}
