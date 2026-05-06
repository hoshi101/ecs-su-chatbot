import os
from dotenv import load_dotenv

def load_frontend_config():
    """
    Loads environment variables relevant to the frontend from the .env file.
    Loads from project root.
    """
    # Load from project root
    load_dotenv()

    return {
        "FASTAPI_BASE_URL": os.getenv("FASTAPI_BASE_URL", "http://localhost:8000"),
        "BOT_NAME": os.getenv("BOT_NAME", "น้องไฟฟ้า (ECS AI Assistant)"),
        "BOT_NAME_EN": os.getenv("BOT_NAME_EN", "N' Faifa"),
        "DOMAIN_NAME": os.getenv("DOMAIN_NAME", "Department of Electrical Engineering, Silpakorn University"),
        "DEFAULT_LLM_PROVIDER": os.getenv("LLM_PROVIDER", "gemini"),
        "DEFAULT_LLM_MODEL": os.getenv("OPENAI_MODEL", "chat-latest")
        if os.getenv("LLM_PROVIDER", "gemini").strip().lower() == "openai"
        else os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    }

# Load config once when the module is imported
FRONTEND_CONFIG = load_frontend_config()
