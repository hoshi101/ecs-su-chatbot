from src.backend.core import response_templates
from src.backend.core.config import BOT_NAME, DOMAIN_NAME


def test_thai_greeting_variants_stay_consistent(monkeypatch):
    for index in range(len(response_templates.GREETING_TEMPLATES)):
        monkeypatch.setattr(response_templates.random, "choice", lambda seq, index=index: seq[index])

        response = response_templates.build_greeting_response("th")

        assert response.startswith("สวัสดีครับ")
        assert BOT_NAME in response
        assert response_templates.THAI_DOMAIN_NAME in response
        assert "Department of Electrical Engineering" not in response
        assert "หลักสูตร" in response
        assert "อาจารย์" in response
        assert "ติดต่อ" in response
        assert "{" not in response
        assert "}" not in response


def test_english_greeting_variants_stay_consistent(monkeypatch):
    for index in range(len(response_templates.GREETING_TEMPLATES_EN)):
        monkeypatch.setattr(response_templates.random, "choice", lambda seq, index=index: seq[index])

        response = response_templates.build_greeting_response("en")

        assert response.startswith("Hello")
        assert response_templates.get_bot_name_for_language("en") in response
        assert DOMAIN_NAME in response
        normalized = response.lower()
        assert any(term in normalized for term in ("curriculum", "course", "lecturer", "contact", "department question"))
        assert "{" not in response
        assert "}" not in response


def test_thai_capability_response_describes_indexed_knowledge():
    response = response_templates.build_capability_response("th")

    assert "ECS" in response
    assert "2565" in response
    assert "147 หน่วยกิต" in response
    assert "146 หน่วยกิต" in response
    assert "คำอธิบายรายวิชา" in response
    assert "ไม่พบข้อมูล" in response


def test_english_capability_response_describes_indexed_knowledge():
    response = response_templates.build_capability_response("en")
    normalized = response.lower()

    assert "ecs" in normalized
    assert "2565" in normalized
    assert "147 credits" in normalized
    assert "146 credits" in normalized
    assert "course details" in normalized
    assert "instead of guessing" in normalized


def test_thai_soft_out_of_scope_generic_closes_are_not_food_specific():
    food_terms = ("กิน", "ข้าว", "อาหาร", "ท้อง")

    for close in response_templates.OUT_OF_SCOPE_SOFT_CLOSES["generic"]:
        assert not any(term in close for term in food_terms)
        assert "ภาควิชา" in close or "หลักสูตร" in close
        assert "ครับ" in close


def test_thai_soft_out_of_scope_themed_closes_cover_distinct_situations():
    expected_terms = {
        "food": ("กิน", "อาหาร", "ท้อง"),
        "rest": ("พัก", "ล้า", "ดูแลตัวเอง"),
        "stress": ("หายใจ", "หนัก", "ดูแลตัวเอง"),
    }

    for theme, terms in expected_terms.items():
        for close in response_templates.OUT_OF_SCOPE_SOFT_CLOSES[theme]:
            assert any(term in close for term in terms)
            assert "ครับ" in close


def test_thai_soft_out_of_scope_response_keeps_original_shape(monkeypatch):
    monkeypatch.setattr(response_templates.random, "choice", lambda seq: seq[0])

    response = response_templates.build_out_of_scope_response(
        variant="soft_oob",
        language="th",
        theme="generic",
    )

    assert response.startswith(response_templates.OUT_OF_SCOPE_SOFT_OPENINGS[0])
    assert response_templates.OUT_OF_SCOPE_SOFT_CLOSES["generic"][0] in response
