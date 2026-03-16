# FSS Hero Chatbot - Restructured

A sophisticated AI-powered chatbot specialized for the Finansia Hero Trading Platform, built with LangGraph, Qdrant, and Gemini AI.

## Project Structure (Restructured)

The project has been systematically restructured for better maintainability and clarity:

```
fsshero-chatbot/
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment template
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
│   │   │   └── agent.py        # HERO Bot agent implementation
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
│   └── process_documents.py     # Document processing script
│
├── tests/                        # Testing infrastructure
│   ├── conftest.py              # Pytest configuration
│   ├── unit/                    # Unit tests
│   │   ├── test_agent.py       # Agent tests (consolidated)
│   │   ├── test_connectivity.py
│   │   └── test_imports.py
│   ├── integration/             # Integration tests
│   │   └── test_api_endpoints.py
│   └── migration/               # Migration tests
│
├── docs/                         # Documentation
│   ├── guides/                  # User guides
│   │   ├── API_TESTING_GUIDE.md
│   │   └── POSTMAN_TESTING_GUIDE.md
│   ├── architecture/            # Architecture docs
│   │   └── SENIOR_ENGINEER_PRESENTATION.md
│   ├── implementation/
│   ├── migration/
│   ├── project-analysis/
│   └── testing/
│
├── data/                         # Document storage
│   ├── home_page/
│   ├── popular_feature_page/
│   └── คู่มือ/
│
├── archive/                      # Archived/reference materials
│
└── README.md                     # This file
```

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to the project
cd fsshero-chatbot

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - QDRANT_API_KEY
# - QDRANT_URL
# - GOOGLE_API_KEY
# - TAVILY_API_KEY
```

### 2. Process Documents (First Run)

```bash
# Process documents and populate vector database
python scripts/process_documents.py
```

### 3. Start the Application

**Option A: Using the startup scripts (Recommended)**

```bash
# Terminal 1: Start backend
python scripts/run_backend.py --reload

# Terminal 2: Start frontend
python scripts/run_frontend.py
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
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Key Features

### HERO Bot Capabilities

- **Specialized Trading Assistant**: Expert knowledge of Finansia Hero Trading Platform
- **Multi-Modal RAG**: Combines internal documentation with external trading resources
- **Query Enhancement**: Automatically improves user questions for better search results
- **Domain-Restricted Search**: Only searches trusted financial sources
- **Real-time Workflow Tracing**: Transparent decision-making process

### Technical Features

- **Advanced Architecture**: LangGraph state machine with Gemini AI
- **Vector Database**: Qdrant with BGE-M3 multilingual embeddings
- **Document Processing**: Supports PDF, CSV, JSON, TXT, and MD files
- **Session Management**: Persistent conversation history
- **Error Handling**: Comprehensive error handling and recovery
- **Configurable Search**: Enable/disable web search as needed

## Development

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
  "enable_web_search": true
}
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

The restructured project maintains all existing functionality with improved test organization:

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_agent.py -v

# Run with coverage
pytest --cov=src tests/
```

## Migration Notes

This restructured version:

- **Preserves all existing functionality**
- **Maintains API compatibility**
- **Improves code organization**
- **Enhances maintainability**
- **Supports future growth**

All original features continue to work exactly as before, with improved organization and clearer structure.

## Environment Variables

Required environment variables in `.env` (at project root):

```bash
# Qdrant Vector Database
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_url
QDRANT_COLLECTION_NAME=fsshero-chatbot-bge-m3

# Google/Gemini AI
GOOGLE_API_KEY=your_google_api_key

# Web Search (Tavily)
TAVILY_API_KEY=your_tavily_api_key

# Frontend Configuration
FASTAPI_BASE_URL=http://localhost:8000

# Optional: Document Processing
DOC_SOURCE_DIR=data

# Optional: HERO Bot Configuration
DOMAIN_NAME=Finansia Hero Trading Platform
BOT_NAME=HERO Bot
SEARCH_DOMAINS=www.finansiahero.com,smartaccess.fnsyrus.com
FINANCIAL_TEMPERATURE=0.3
ENABLE_QUERY_ENHANCEMENT=true
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **User Guides**: `docs/guides/` - API testing and Postman guides
- **Architecture**: `docs/architecture/` - Technical architecture and design docs
- **Implementation**: `docs/implementation/` - Implementation details and plans
- **Testing**: `docs/testing/` - Test plans and reports

## Contributing

1. Follow the established directory structure
2. Add tests for new functionality in appropriate test directories
3. Update documentation as needed
4. Ensure all imports use the new structure paths
5. Keep environment variables in `.env` file at root
6. Run tests before submitting changes

## License

This project maintains the same license as the original implementation.

---

**The FSS Hero Chatbot has been successfully restructured for better maintainability and future growth!**
