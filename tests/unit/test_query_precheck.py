from langchain_core.messages import HumanMessage

from src.backend.core import agent
from src.backend.core.agent import (
    build_answer_prompt,
    classify_query_precheck,
    has_course_code,
    router_node,
    should_enhance_query,
    should_prefer_local_rag,
    should_prefer_web_for_public_updates,
)


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


def test_short_english_contact_channel_query_still_shortcuts():
    intent, _ = classify_query_precheck("What is the department phone number?")
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


def test_english_greeting_phrase_still_shortcuts():
    intent, _ = classify_query_precheck("Good morning!")
    assert intent == "greeting"


def test_english_greeting_with_there_still_shortcuts():
    intent, _ = classify_query_precheck("hi there")
    assert intent == "greeting"


def test_thai_greeting_variant_still_shortcuts():
    intent, _ = classify_query_precheck("ฮัลโหล")
    assert intent == "greeting"


def test_repeated_thai_greeting_marker_still_shortcuts():
    intent, _ = classify_query_precheck("สวัสดีๆ")
    assert intent == "greeting"


def test_greeting_with_emoji_still_shortcuts():
    intent, _ = classify_query_precheck("สวัสดีครับ 😊")
    assert intent == "greeting"


def test_greeting_plus_real_question_does_not_shortcut():
    intent, _ = classify_query_precheck("สวัสดี ขอข้อมูลติดต่อภาควิชาหน่อย")
    assert intent == "domain_question"


def test_knowledge_inventory_question_shortcuts_to_capability():
    for query in (
        "น้องไฟฟ้ามีเอกสารอะไรบ้างในระบบ",
        "มีข้อมูลอะไรในระบบ",
        "รู้อะไรบ้าง",
        "What documents do you have?",
    ):
        intent, _ = classify_query_precheck(query)
        assert intent == "capability"


def test_specific_information_inventory_question_uses_domain_flow():
    intent, _ = classify_query_precheck("หลักสูตรปริญญาโทวิศวกรรมไฟฟ้าและคอมพิวเตอร์มีข้อมูลอะไรบ้าง")
    assert intent == "domain_question"


def test_course_code_information_question_uses_domain_flow():
    intent, _ = classify_query_precheck("รหัสวิชา SU115 อาหารเพื่อสุขภาพ มีข้อมูลอะไรบ้าง")
    assert intent == "domain_question"


def test_numeric_course_code_information_question_uses_domain_flow():
    intent, _ = classify_query_precheck("511 104 แคลคูลัสสำหรับวิศวกร 1 มีข้อมูลอะไรบ้าง")
    assert intent == "domain_question"


def test_course_code_detector_supports_common_formats():
    assert has_course_code("รหัสวิชา SU115 อาหารเพื่อสุขภาพ")
    assert has_course_code("511 104 แคลคูลัสสำหรับวิศวกร 1")
    assert has_course_code("511-104 แคลคูลัสสำหรับวิศวกร 1")
    assert has_course_code("รหัสวิชา 511104 แคลคูลัสสำหรับวิศวกร 1")
    assert has_course_code("618362 คือวิชาอะไร")
    assert has_course_code("618362 กี่หน่วยกิต")
    assert not has_course_code("หลักสูตรปี 2565 รวม 147 หน่วยกิต")


def test_course_code_queries_prefer_local_rag():
    assert should_prefer_local_rag("รหัสวิชา SU115 อาหารเพื่อสุขภาพ")
    assert should_prefer_local_rag("511 104 แคลคูลัสสำหรับวิศวกร 1")
    assert should_prefer_local_rag("618362 คือวิชาอะไร")
    assert should_prefer_local_rag("618362 กี่หน่วยกิต")


def test_compact_numeric_course_code_questions_use_domain_flow():
    for query in ("618362 คือวิชาอะไร", "618362 กี่หน่วยกิต"):
        intent, _ = classify_query_precheck(query)
        assert intent == "domain_question"


def test_internship_hour_question_uses_domain_flow_and_local_rag():
    query = "วิชา ฝึกงาน ต้องไม่น้อยกว่ากี่ชั่วโมง"
    intent, _ = classify_query_precheck(query)

    assert intent == "domain_question"
    assert should_prefer_local_rag(query)


def test_english_greeting_plus_real_question_does_not_shortcut():
    intent, _ = classify_query_precheck("Hello, what is the department phone number?")
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


def test_institution_related_non_ee_query_stays_in_scope():
    intent, _ = classify_query_precheck("ภาควิชาวิศวกรรมเครื่องกลอยู่ตึกไหน")
    assert intent == "domain_question"


def test_institution_related_unknown_query_stays_in_scope():
    intent, _ = classify_query_precheck("ช่วยบอกคะแนนขั้นต่ำรอบล่าสุดของคณะให้หน่อย")
    assert intent == "domain_question"


def test_specific_query_skips_enhancement():
    should_enhance, _ = should_enhance_query(
        "ขอข้อมูลติดต่อภาควิชาวิศวกรรมไฟฟ้า มหาวิทยาลัยศิลปากร เบอร์โทร อีเมล ที่อยู่สำนักงาน"
    )
    assert should_enhance is False


def test_public_update_queries_prefer_web_search():
    for query in (
        "รับสมัครเมื่อไหร่",
        "TCAS รอบล่าสุดใช้คะแนนเท่าไร",
        "คะแนนขั้นต่ำปีนี้ของคณะคือเท่าไร",
        "latest admission deadline",
    ):
        assert should_prefer_web_for_public_updates(query) is True


def test_stable_curriculum_queries_do_not_force_web_search():
    for query in (
        "หลักสูตร ECS รวมกี่หน่วยกิต",
        "ประธานหลักสูตร ECS คือใคร",
        "ภาควิชามีหลักสูตรปริญญาตรีอะไรบ้าง",
    ):
        assert should_prefer_web_for_public_updates(query) is False


def test_answer_prompt_requires_partial_answer_before_missing_notice():
    prompt = build_answer_prompt(
        {
            "messages": [HumanMessage(content="หลักสูตร ECS มีข้อมูลอะไรบ้างและ prerequisite คืออะไร")],
            "original_query": "หลักสูตร ECS มีข้อมูลอะไรบ้างและ prerequisite คืออะไร",
            "enhanced_query": "หลักสูตร ECS prerequisite",
            "response_language": "th",
            "rag": "[Source 1: program_ecs.md]\nหลักสูตร ECS พ.ศ. 2565 รวม 147 หน่วยกิต",
            "web": "",
        }
    )

    assert "answer the supported parts first" in prompt
    assert "which specific detail was not found" in prompt
    assert "Do not say broadly that information was not found" in prompt


def test_answer_prompt_mentions_source_url_when_context_has_url():
    prompt = build_answer_prompt(
        {
            "messages": [HumanMessage(content="หลักสูตรไฟฟ้าสื่อสารกี่หน่วยกิต")],
            "original_query": "หลักสูตรไฟฟ้าสื่อสารกี่หน่วยกิต",
            "enhanced_query": "หลักสูตรไฟฟ้าสื่อสาร หน่วยกิต",
            "response_language": "th",
            "rag": "[Source 1: program_electrical_communications.md]\nSource URL: https://ee-eng.su.ac.th/Program.aspx?Course=ElectricalCommunicationsEngineering\nจำนวนไม่น้อยกว่า 146 หน่วยกิต",
            "web": "",
        }
    )

    assert "แหล่งอ้างอิง" in prompt
    assert "URL" in prompt


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

    for query in (
        "ขอข้อมูลการติดต่อภาควิชาหน่อยครับ",
        "ขอเบอร์โทรภาควิชา",
        "facebook ภาควิชา",
        "What is the department phone number?",
    ):
        state = {
            "messages": [HumanMessage(content=query)],
            "llm_provider": "openai",
            "llm_model": "gpt-5.4-mini",
        }
        result = router_node(state)

        assert result["route"] == "end"
        assert result["precheck_intent"] == "contact"
        if "facebook" in query.lower():
            assert "Facebook" in result["messages"][-1].content
        elif agent.detect_query_language(query) == "en":
            assert "Phone" in result["messages"][-1].content
        else:
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

    for query in ("สวัสดีครับ", "สวัสดีครับผม", "Hello!!", "หวัดดีจ้า", "Good morning!", "hi there", "ฮัลโหล", "สวัสดีๆ"):
        state = {
            "messages": [HumanMessage(content=query)],
            "llm_provider": "openai",
            "llm_model": "gpt-5.4-mini",
        }
        result = router_node(state)

        assert result["route"] == "end"
        assert result["precheck_intent"] == "greeting"
        assert result["messages"][-1].content


def test_mixed_intent_does_not_call_shortcut_llm(monkeypatch):
    class DummyStructured:
        def invoke(self, _messages):
            return agent.RouteDecision(route="answer", reply="Handled by normal flow")

    class DummyLLM:
        def with_structured_output(self, _schema):
            return DummyStructured()

    monkeypatch.setattr(agent, "build_chat_model", lambda *args, **kwargs: DummyLLM())

    state = {
        "messages": [HumanMessage(content="Hello, what is the department phone number?")],
        "llm_provider": "openai",
        "llm_model": "gpt-5.4-mini",
    }
    result = router_node(state)

    assert result["route"] == "answer"
    assert result["precheck_intent"] == "domain_question"


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
