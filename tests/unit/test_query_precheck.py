from src.backend.core.agent import classify_query_precheck, should_enhance_query


def test_contact_query_shortcuts_to_template():
    intent, _ = classify_query_precheck("ขอข้อมูลติดต่อภาควิชาหน่อย")
    assert intent == "contact"


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
