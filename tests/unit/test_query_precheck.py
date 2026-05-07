from langchain_core.messages import HumanMessage

from src.backend.core import agent
from src.backend.core.agent import classify_query_precheck, router_node, should_enhance_query


def test_contact_query_shortcuts_to_template():
    intent, _ = classify_query_precheck("ขอข้อมูลติดต่อภาควิชาหน่อย")
    assert intent == "contact"


def test_long_contact_query_goes_to_domain_flow():
    intent, _ = classify_query_precheck(
        "ขอข้อมูลติดต่อภาควิชาวิศวกรรมไฟฟ้า มหาวิทยาลัยศิลปากร พร้อมอีเมลและที่อยู่สำนักงาน"
    )
    assert intent == "domain_question"


def test_greeting_shortcuts_to_template():
    intent, _ = classify_query_precheck("สวัสดี")
    assert intent == "greeting"


def test_out_of_scope_shortcuts_to_template():
    intent, _ = classify_query_precheck("กินข้าวยัง")
    assert intent == "out_of_scope"


def test_domain_query_continues_to_rag_flow():
    intent, _ = classify_query_precheck("หลักสูตรสาขามี prerequisite ไหม")
    assert intent == "domain_question"


def test_specific_query_skips_enhancement():
    should_enhance, _ = should_enhance_query(
        "ขอข้อมูลติดต่อภาควิชาวิศวกรรมไฟฟ้า มหาวิทยาลัยศิลปากร เบอร์โทร อีเมล ที่อยู่สำนักงาน"
    )
    assert should_enhance is False


def test_contact_shortcut_does_not_call_llm(monkeypatch):
    def fail_build_chat_model(*args, **kwargs):
        raise AssertionError("LLM should not be called for contact shortcut")

    monkeypatch.setattr(agent, "build_chat_model", fail_build_chat_model)
    monkeypatch.setattr(agent.random, "choice", lambda seq: seq[0])

    state = {
        "messages": [HumanMessage(content="ขอข้อมูลติดต่อภาควิชาหน่อย")],
        "llm_provider": "openai",
        "llm_model": "gpt-5.4-mini",
    }
    result = router_node(state)

    assert result["route"] == "end"
    assert result["precheck_intent"] == "contact"
    assert "โทรศัพท์" in result["messages"][-1].content


def test_greeting_shortcut_does_not_call_llm(monkeypatch):
    def fail_build_chat_model(*args, **kwargs):
        raise AssertionError("LLM should not be called for greeting shortcut")

    monkeypatch.setattr(agent, "build_chat_model", fail_build_chat_model)
    monkeypatch.setattr(agent.random, "choice", lambda seq: seq[0])

    state = {
        "messages": [HumanMessage(content="สวัสดี")],
        "llm_provider": "openai",
        "llm_model": "gpt-5.4-mini",
    }
    result = router_node(state)

    assert result["route"] == "end"
    assert result["precheck_intent"] == "greeting"
    assert "สวัสดี" in result["messages"][-1].content


def test_out_of_scope_shortcut_does_not_call_llm(monkeypatch):
    def fail_build_chat_model(*args, **kwargs):
        raise AssertionError("LLM should not be called for out-of-scope shortcut")

    monkeypatch.setattr(agent, "build_chat_model", fail_build_chat_model)
    monkeypatch.setattr(agent.random, "choice", lambda seq: seq[0])

    state = {
        "messages": [HumanMessage(content="กินข้าวยัง")],
        "llm_provider": "openai",
        "llm_model": "gpt-5.4-mini",
    }
    result = router_node(state)

    assert result["route"] == "end"
    assert result["precheck_intent"] == "out_of_scope"
    assert "ขออภัย" in result["messages"][-1].content
