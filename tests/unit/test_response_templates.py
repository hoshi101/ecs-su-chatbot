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
