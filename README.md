# EE Support Chatbot

An AI-powered department support chatbot for Electrical Engineering / Electronic and Computer Systems Engineering, built with LangGraph, Qdrant, and switchable Gemini/OpenAI chat models.

## Project Structure

```
ecs-chatbot/
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment template
├── Dockerfile                    # Container image for backend/frontend
├── docker-compose.yml            # Local Docker Compose stack
├── .python-version               # Python version
├── pyproject.toml                # Project metadata
├── requirements.txt              # Python dependencies
│
├── src/                           # Main application source code
│   ├── backend/                  # Backend services
│   │   ├── api/                 # API layer
│   │   │   └── main.py         # FastAPI application
│   │   ├── core/                # Core business logic
│   │   │   ├── config.py       # Configuration management
│   │   │   └── agent.py        # Department assistant agent implementation
│   │   ├── services/            # Service layer
│   │   │   ├── vectorstore.py  # Vector database operations
│   │   │   └── document_processor.py
│   │   └── utils/               # Backend utilities
│   └── frontend/                # Frontend application
│       ├── app.py               # Main Streamlit app
│       ├── components/          # UI components
│       │   └── ui_components.py
│       ├── api/                 # API communication layer
│       │   └── backend_client.py
│       ├── config/              # Configuration management
│       │   └── settings.py     # Frontend settings
│       └── state/               # State management
│           └── session_manager.py
│
├── scripts/                      # Development and utility scripts
│   ├── run_backend.py           # Backend server launcher
│   ├── run_frontend.py          # Frontend server launcher
│   ├── process_documents.py     # Document processing script
│   ├── scrape_department_sources.py
│   └── preflight_check.py
│
├── tests/                        # Testing infrastructure
│   ├── conftest.py              # Pytest configuration
│   ├── unit/                    # Unit tests
│   │   ├── test_agent.py       # Agent tests (consolidated)
│   │   ├── test_llm_config.py
│   │   ├── test_gemini_structured.py
│   │   └── test_query_precheck.py
│   ├── integration/             # Integration tests
│   │   └── test_api_endpoints.py
│   └── migration/               # Migration tests
│
├── docs/                         # Documentation
│   ├── guides/                  # User guides
│   │   ├── API_TESTING_GUIDE.md
│   │   └── POSTMAN_TESTING_GUIDE.md
│   ├── implementation/
│   ├── operations/
│   └── testing/
│
├── data/                         # Document storage
│   ├── web/                     # Scraped official web content
│   ├── มคอ.2.pdf
│   └── รายละเอียดของหลักสูตร_2565.pdf
│
├── bruno/                        # Bruno API collection
│
└── README.md                     # This file
```

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to the project
cd ecs-chatbot

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - QDRANT_API_KEY
# - QDRANT_URL
# - GOOGLE_API_KEY
# - OPENAI_API_KEY
# - TAVILY_API_KEY
#
# Optional defaults:
# - LLM_PROVIDER=openai|gemini
# - GEMINI_MODEL=gemini-2.5-flash
# - OPENAI_MODEL=<your preferred OpenAI chat model>
```

### 2. Process Documents (First Run)

```bash
# Optional but recommended: scrape official department/faculty pages first
.venv/bin/python scripts/scrape_department_sources.py

# Process documents and populate vector database
.venv/bin/python scripts/process_documents.py
```

### 3. Start the Application

**Option A: Using the startup scripts (Recommended)**

```bash
# Terminal 1: Start backend
.venv/bin/python scripts/run_backend.py --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Start frontend
.venv/bin/python scripts/run_frontend.py
```

**Option B: Direct commands**

```bash
# Terminal 1: Start backend
cd src/backend && uvicorn api.main:app --reload

# Terminal 2: Start frontend
cd src/frontend && streamlit run app.py
```

### 4. Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## Docker

Docker support is included for local review and demos. The Compose stack runs
the FastAPI backend and Streamlit frontend as separate services using the same
project image.

```bash
# Build and start backend + frontend
docker compose up --build
```

If your Docker installation uses the legacy Compose plugin, use:

```bash
docker-compose up --build
```

The stack reads runtime configuration from `.env`, so create it from the sample
first and add your local API credentials:

```bash
cp .env.example .env
```

Docker endpoints:

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

Useful Docker commands:

```bash
# Stop containers
docker compose down

# Rebuild after dependency changes
docker compose build --no-cache

# Run tests in the image
docker compose run --rm backend python -m pytest

# Process documents from the mounted ./data directory
docker compose run --rm backend python scripts/process_documents.py
```

## Key Features

### Assistant Capabilities

- **Department Support Assistant**: Answers questions about curriculum, lecturers, regulations, and department services
- **RAG-First Workflow**: Prioritizes local official documents and scraped department/faculty content
- **Query Enhancement**: Rewrites vague user questions into stronger knowledge base searches
- **Official Website Fallback**: Searches trusted department/faculty domains when local context is insufficient
- **Workflow Tracing**: Exposes routing and retrieval steps for debugging and demo transparency

### Technical Features

- **Advanced Architecture**: LangGraph state machine with selectable Gemini or OpenAI chat models
- **Vector Database**: Qdrant with BGE-M3 multilingual embeddings
- **Document Processing**: Supports PDF, CSV, JSON, TXT, and MD files
- **Session Management**: Persistent conversation history
- **Error Handling**: Comprehensive error handling and recovery
- **Configurable Search**: Enable/disable web search as needed
- **Provider Switching**: Choose provider and model from the Streamlit sidebar at runtime

## Development

### Knowledge Base Collection

For this project, official department and faculty pages should be collected into
the local knowledge base instead of relying on live web search for every query.

Use:

```bash
.venv/bin/python scripts/scrape_department_sources.py
```

This writes cleaned Markdown/JSON into `data/web/clean/`. Raw scrape output and
downloaded source files are ignored for public releases. See
`docs/guides/WEB_SCRAPING_GUIDE.md`.

### Project Structure Benefits

1. **Clear Separation of Concerns**: API, business logic, services, and utilities are properly separated
2. **Scalable Organization**: Structure can grow with the project without becoming unwieldy
3. **Easy Navigation**: Developers can quickly find and modify specific functionality
4. **Testing Support**: Clear testing hierarchy supports comprehensive test coverage
5. **Maintainability**: Logical organization makes code maintenance easier

### Adding New Features

1. **Backend Features**: Add to appropriate directories in `src/backend/`
2. **Frontend Components**: Add to `src/frontend/components/`
3. **API Endpoints**: Extend `src/backend/api/main.py`
4. **Services**: Add new services to `src/backend/services/`
5. **Configuration**: Update `src/backend/core/config.py` and `.env`

## API Endpoints

### Chat Endpoint
```
POST /chat/
{
  "session_id": "string",
  "query": "string",
  "enable_web_search": true,
  "llm_provider": "gemini",
  "llm_model": "gemini-2.5-flash"
}
```

### LLM Options Endpoint
```
GET /llm/options
```

### Document Upload
```
POST /upload-document/
Content-Type: multipart/form-data
file: PDF file
```

### Health Check
```
GET /health
```

## Testing

Run the automated test suite with pytest:

```bash
# Run all tests
.venv/bin/python -m pytest

# Run unit tests only
.venv/bin/python -m pytest tests/unit/

# Run integration tests only
.venv/bin/python -m pytest tests/integration/ -v

# Run specific test file
.venv/bin/python -m pytest tests/unit/test_agent.py -v

# Run with coverage
.venv/bin/python -m pytest --cov=src tests/
```

Live service diagnostics are available as manual scripts and require valid `.env`
credentials for Qdrant, Gemini/OpenAI, and Tavily:

```bash
.venv/bin/python scripts/verify_imports.py
.venv/bin/python scripts/check_connectivity.py
```

## Environment Variables

Required environment variables in `.env` (at project root):

```bash
# Qdrant Vector Database
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_url
QDRANT_COLLECTION_NAME=ecs-su-chatbot-bge-m3

# Google/Gemini AI
GOOGLE_API_KEY=your_google_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-5.4-mini
GEMINI_MODEL=gemini-2.5-flash

# Web Search (Tavily)
TAVILY_API_KEY=your_tavily_api_key

# Frontend Configuration
FASTAPI_BASE_URL=http://localhost:8001

# Optional: Document Processing
DOC_SOURCE_DIR=data

# Optional: Assistant Configuration
DOMAIN_NAME=Department of Electrical Engineering, Silpakorn University
BOT_NAME=น้องไฟฟ้า (ECS AI Assistant)
BOT_NAME_EN=N' Faifa
SEARCH_DOMAINS=ee-eng.su.ac.th,eng2.su.ac.th
FINANCIAL_TEMPERATURE=0.2
ENABLE_QUERY_ENHANCEMENT=true
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **User Guides**: `docs/guides/` - API testing and Postman guides
- **Operations**: `docs/operations/` - Debugging and release-readiness notes
- **Testing**: `docs/testing/` - Routing guides and question sets

## Contributing

1. Follow the established directory structure
2. Add tests for new functionality in appropriate test directories
3. Update documentation as needed
4. Ensure all imports use the new structure paths
5. Keep environment variables in `.env` file at root
6. Run tests before submitting changes

## License

This project maintains the same license as the original implementation.
