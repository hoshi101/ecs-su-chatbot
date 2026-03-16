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
        "FASTAPI_BASE_URL": os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
    }

# Load config once when the module is imported
FRONTEND_CONFIG = load_frontend_config()