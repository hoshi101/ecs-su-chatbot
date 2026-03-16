import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# === NEW: Qdrant Vector Database Configuration ===
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "fsshero-chatbot-bge-m3")

# === NEW: Google/Gemini Configuration ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# === EXISTING: Tavily (keeping for parity) ===
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# === NEW: BGE-M3 Embedding Model ===
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIMENSIONS = 1024  # BGE-M3 embedding dimensions

# === LEGACY: Old configurations (commented for potential rollback) ===
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT","us-east-1")
# PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-index")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# OLD_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 384 dimensions

# === EXISTING: Paths ===
DOC_SOURCE_DIR = os.getenv("DOC_SOURCE_DIR", "data")

# === NEW: HERO Bot Domain-Specific Configuration ===
DOMAIN_NAME = os.getenv("DOMAIN_NAME", "Finansia Hero Trading Platform")
BOT_NAME = os.getenv("BOT_NAME", "HERO Bot")
SEARCH_DOMAINS = os.getenv("SEARCH_DOMAINS", "www.finansiahero.com,smartaccess.fnsyrus.com/open-board/").split(',')

# HERO Bot Specialization Areas (identical to original HERO Bot)
SPECIALTY_AREAS = [
    "Platform features and navigation",
    "Trading tools and order management",
    "Technical analysis and charting",
    "Account management and settings",
    "Risk management and trading strategies",
    "Troubleshooting platform issues"
]

# HERO Bot Response Settings
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("DEFAULT_SIMILARITY_THRESHOLD", "0.7"))
FINANCIAL_TEMPERATURE = float(os.getenv("FINANCIAL_TEMPERATURE", "0.3"))
ENABLE_QUERY_ENHANCEMENT = os.getenv("ENABLE_QUERY_ENHANCEMENT", "true").lower() == "true"