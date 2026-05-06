import pytest

from src.backend.core import config


def test_normalize_provider_accepts_supported_values():
    assert config.normalize_provider("gemini") == "gemini"
    assert config.normalize_provider("OPENAI") == "openai"


def test_normalize_provider_rejects_unsupported_values():
    with pytest.raises(ValueError):
        config.normalize_provider("anthropic")


def test_resolve_model_name_uses_provider_defaults():
    assert config.resolve_model_name("gemini") == config.GEMINI_MODEL
    assert config.resolve_model_name("openai") == config.OPENAI_MODEL


def test_resolve_model_name_preserves_explicit_model():
    assert config.resolve_model_name("openai", "gpt-5.5") == "gpt-5.5"
