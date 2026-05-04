import os
from dotenv import load_dotenv

# Load environment variables from .env file at project root
load_dotenv()

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

# === EXISTING: Paths ===
DOC_SOURCE_DIR = os.getenv("DOC_SOURCE_DIR", "data")
WEB_CONTENT_DIR = os.getenv("WEB_CONTENT_DIR", "data/web/clean")

# === Department Domain Configuration ===
DOMAIN_NAME = os.getenv("DOMAIN_NAME", "Department of Electrical Engineering, Silpakorn University")
BOT_NAME = os.getenv("BOT_NAME", "EE Support Assistant")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "th")
SEARCH_DOMAINS = [
    domain.strip()
    for domain in os.getenv("SEARCH_DOMAINS", "ee-eng.su.ac.th,eng2.su.ac.th").split(",")
    if domain.strip()
]
FACULTY_CONTACT_TEXT = os.getenv(
    "FACULTY_CONTACT_TEXT",
    "โทรศัพท์ 034-219364-66 ต่อ 25520, 089-979-7911, โทรศัพท์/โทรสาร 034-241971, Facebook: Department of Electrical Engineering - Silpakorn University"
)
SENSITIVE_TOPIC_POLICY = os.getenv(
    "SENSITIVE_TOPIC_POLICY",
    "Do not provide personal or sensitive information that is not clearly available in official public sources."
)

SPECIALTY_AREAS = [
    "Curriculum and degree program information",
    "Course information and prerequisite guidance",
    "Lecturer and staff directory information from official sources",
    "Academic regulations, forms, and department procedures",
    "Internship, cooperative education, and student services",
    "Department contact information and general guidance"
]

# Response Settings
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("DEFAULT_SIMILARITY_THRESHOLD", "0.7"))
FINANCIAL_TEMPERATURE = float(os.getenv("FINANCIAL_TEMPERATURE", "0.2"))
ENABLE_QUERY_ENHANCEMENT = os.getenv("ENABLE_QUERY_ENHANCEMENT", "true").lower() == "true"

# === NEW: Document Processing Configuration ===
DOC_CHUNK_SIZE = int(os.getenv("DOC_CHUNK_SIZE", "1000"))
DOC_CHUNK_OVERLAP = int(os.getenv("DOC_CHUNK_OVERLAP", "200"))
DOC_SUPPORTED_FORMATS = os.getenv("DOC_SUPPORTED_FORMATS", "pdf,csv,json,txt,md").split(',')
DOC_MAX_UPLOAD_SIZE = int(os.getenv("DOC_MAX_UPLOAD_SIZE", "52428800"))  # 50MB default

# === Rate Limiting Configuration ===
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
RATE_LIMIT_STRATEGY = os.getenv("RATE_LIMIT_STRATEGY", "fixed-window")  # or "moving-window"
