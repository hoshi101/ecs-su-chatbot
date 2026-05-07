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


def test_contact_with_polite_suffix_still_shortcuts():
    intent, _ = classify_query_precheck("ขอข้อมูลการติดต่อภาควิชาหน่อยครับ")
    assert intent == "contact"


def test_short_contact_channel_query_still_shortcuts():
    intent, _ = classify_query_precheck("ขอเบอร์โทรภาควิชา")
    assert intent == "contact"


def test_specific_contact_query_does_not_shortcut():
    intent, _ = classify_query_precheck("ขอข้อมูลติดต่ออาจารย์ประจำสาขาพร้อมอีเมล")
    assert intent == "domain_question"


def test_greeting_shortcuts_to_template():
    intent, _ = classify_query_precheck("สวัสดี")
    assert intent == "greeting"


def test_greeting_with_polite_suffix_still_shortcuts():
    intent, _ = classify_query_precheck("สวัสดีครับผม")
    assert intent == "greeting"


def test_english_greeting_with_punctuation_still_shortcuts():
    intent, _ = classify_query_precheck("Hello!!")
    assert intent == "greeting"


def test_greeting_plus_real_question_does_not_shortcut():
    intent, _ = classify_query_precheck("สวัสดี ขอข้อมูลติดต่อภาควิชาหน่อย")
    assert intent == "domain_question"


def test_out_of_scope_shortcuts_to_template():
    intent, _ = classify_query_precheck("กินข้าวยัง")
    assert intent == "out_of_scope"


def test_soft_out_of_scope_semantic_query_shortcuts():
    intent, _ = classify_query_precheck("หิวข้าวจัง")
    assert intent == "out_of_scope"


def test_hard_out_of_scope_semantic_query_shortcuts():
    intent, _ = classify_query_precheck("ใครคือนายก")
    assert intent == "out_of_scope"


def test_out_of_scope_with_polite_suffix_still_shortcuts():
    intent, _ = classify_query_precheck("เล่าเรื่องตลกหน่อยครับ")
    assert intent == "out_of_scope"


def test_out_of_scope_question_with_punctuation_still_shortcuts():
    intent, _ = classify_query_precheck("สรุปข่าว!!")
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


def test_repeated_contact_variants_do_not_call_llm(monkeypatch):
    def fail_build_chat_model(*args, **kwargs):
        raise AssertionError("LLM should not be called for contact shortcut")

    monkeypatch.setattr(agent, "build_chat_model", fail_build_chat_model)
    monkeypatch.setattr(agent.random, "choice", lambda seq: seq[0])

    for query in ("ขอข้อมูลการติดต่อภาควิชาหน่อยครับ", "ขอเบอร์โทรภาควิชา", "facebook ภาควิชา"):
        state = {
            "messages": [HumanMessage(content=query)],
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


def test_repeated_greeting_variants_do_not_call_llm(monkeypatch):
    def fail_build_chat_model(*args, **kwargs):
        raise AssertionError("LLM should not be called for greeting shortcut")

    monkeypatch.setattr(agent, "build_chat_model", fail_build_chat_model)
    monkeypatch.setattr(agent.random, "choice", lambda seq: seq[0])

    for query in ("สวัสดีครับ", "สวัสดีครับผม", "Hello!!", "หวัดดีจ้า"):
        state = {
            "messages": [HumanMessage(content=query)],
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
    assert "ภาควิชา" in result["messages"][-1].content or "ขอโทษ" in result["messages"][-1].content


def test_repeated_out_of_scope_variants_do_not_call_llm(monkeypatch):
    def fail_build_chat_model(*args, **kwargs):
        raise AssertionError("LLM should not be called for out-of-scope shortcut")

    monkeypatch.setattr(agent, "build_chat_model", fail_build_chat_model)
    monkeypatch.setattr(agent.random, "choice", lambda seq: seq[0])

    for query in ("กินไรดี", "เล่าเรื่องตลกหน่อยครับ", "สรุปข่าว!!", "หิวข้าวจัง", "ใครคือนายก"):
        state = {
            "messages": [HumanMessage(content=query)],
            "llm_provider": "openai",
            "llm_model": "gpt-5.4-mini",
        }
        result = router_node(state)

        assert result["route"] == "end"
        assert result["precheck_intent"] == "out_of_scope"
        assert result["messages"][-1].content
