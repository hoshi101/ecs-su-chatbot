import uuid

from fastapi.testclient import TestClient

from src.backend.api.main import app


def test_chat_endpoint_uses_current_query_with_same_session():
    app.state.limiter.enabled = False
    client = TestClient(app)
    session_id = f"same-session-{uuid.uuid4()}"

    cases = [
        ("สวัสดีครับ", "greeting"),
        ("ขอเบอร์โทรภาควิชา", "contact"),
        ("น้องไฟฟ้ามีข้อมูลอะไรบ้างในระบบ", "capability"),
        ("วันนี้ฝนจะตกไหม", "out_of_scope"),
    ]

    for query, expected_intent in cases:
        response = client.post(
            "/chat/",
            json={
                "session_id": session_id,
                "query": query,
                "enable_web_search": True,
                "force_web_search": False,
                "similarity_threshold": 0.7,
                "llm_provider": "openai",
                "llm_model": "gpt-5.4-mini",
            },
        )
        payload = response.json()
        first_event = payload["trace_events"][0]

        assert response.status_code == 200
        assert first_event["details"]["precheck_intent"] == expected_intent
