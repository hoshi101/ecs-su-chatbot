#!/usr/bin/env python3
"""
Comprehensive import and configuration testing script.
Tests all critical imports and verifies system components.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_import_checks():
    """Test all critical imports systematically."""
    print("=" * 80)
    print("TESTING CRITICAL IMPORTS")
    print("=" * 80)

    test_results = []

    # Test 1: Environment variables
    print("\n[1/10] Testing environment variables...")
    try:
        from src.backend.core.config import (
            QDRANT_API_KEY, QDRANT_URL, QDRANT_COLLECTION_NAME,
            GOOGLE_API_KEY, TAVILY_API_KEY,
            EMBED_MODEL, EMBED_DIMENSIONS
        )
        assert QDRANT_API_KEY, "QDRANT_API_KEY is not set"
        assert QDRANT_URL, "QDRANT_URL is not set"
        assert GOOGLE_API_KEY, "GOOGLE_API_KEY is not set"
        assert TAVILY_API_KEY, "TAVILY_API_KEY is not set"
        print(f"   ✓ All API keys loaded successfully")
        print(f"   ✓ Collection: {QDRANT_COLLECTION_NAME}")
        print(f"   ✓ Embed Model: {EMBED_MODEL}")
        print(f"   ✓ Embed Dimensions: {EMBED_DIMENSIONS}")
        test_results.append(("Environment Variables", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Environment Variables", f"FAIL: {e}"))
        return test_results

    # Test 2: Qdrant client
    print("\n[2/10] Testing Qdrant client...")
    try:
        from src.backend.services.vectorstore import _get_qdrant_client
        client = _get_qdrant_client()
        print(f"   ✓ Qdrant client initialized successfully")
        test_results.append(("Qdrant Client", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Qdrant Client", f"FAIL: {e}"))
        return test_results

    # Test 3: BGE-M3 embeddings
    print("\n[3/10] Testing BGE-M3 embeddings...")
    try:
        from src.backend.services.vectorstore import embeddings
        print(f"   ✓ BGE-M3 embeddings initialized successfully")
        test_results.append(("BGE-M3 Embeddings", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("BGE-M3 Embeddings", f"FAIL: {e}"))
        return test_results

    # Test 4: Vectorstore retriever
    print("\n[4/10] Testing vectorstore retriever...")
    try:
        from src.backend.services.vectorstore import get_retriever
        retriever = get_retriever()
        print(f"   ✓ Vectorstore retriever initialized successfully")
        test_results.append(("Vectorstore Retriever", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Vectorstore Retriever", f"FAIL: {e}"))
        return test_results

    # Test 5: Document processor
    print("\n[5/10] Testing document processor...")
    try:
        from src.backend.services.document_processor import document_processor
        assert document_processor is not None
        print(f"   ✓ Document processor initialized successfully")
        print(f"   ✓ Supported formats: {document_processor.supported_formats}")
        test_results.append(("Document Processor", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Document Processor", f"FAIL: {e}"))
        return test_results

    # Test 6: Agent and LLMs
    print("\n[6/10] Testing RAG agent...")
    try:
        from src.backend.core.agent import rag_agent, enhance_query_hero_bot_style
        assert rag_agent is not None
        print(f"   ✓ RAG agent initialized successfully")
        print(f"   ✓ Query enhancement function available")
        test_results.append(("RAG Agent", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("RAG Agent", f"FAIL: {e}"))
        return test_results

    # Test 7: FastAPI backend
    print("\n[7/10] Testing FastAPI backend...")
    try:
        from src.backend.api.main import app
        assert app is not None
        print(f"   ✓ FastAPI app initialized successfully")
        test_results.append(("FastAPI Backend", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("FastAPI Backend", f"FAIL: {e}"))
        return test_results

    # Test 8: Frontend imports
    print("\n[8/10] Testing frontend imports...")
    try:
        from src.frontend.config.settings import FRONTEND_CONFIG
        from src.frontend.state.session_manager import init_session_state
        from src.frontend.api.backend_client import chat_with_backend_agent
        print(f"   ✓ Frontend modules imported successfully")
        print(f"   ✓ Backend URL: {FRONTEND_CONFIG.get('FASTAPI_BASE_URL')}")
        test_results.append(("Frontend Imports", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Frontend Imports", f"FAIL: {e}"))
        return test_results

    # Test 9: LangChain imports
    print("\n[9/10] Testing LangChain imports...")
    try:
        from langchain_core.messages import HumanMessage, AIMessage
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_tavily import TavilySearch
        from langgraph.graph import StateGraph, END
        from langgraph.checkpoint.memory import MemorySaver
        print(f"   ✓ LangChain modules imported successfully")
        test_results.append(("LangChain Imports", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("LangChain Imports", f"FAIL: {e}"))
        return test_results

    # Test 10: Rate limiting
    print("\n[10/10] Testing rate limiting imports...")
    try:
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        print(f"   ✓ Rate limiting modules imported successfully")
        test_results.append(("Rate Limiting", "PASS"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Rate Limiting", f"FAIL: {e}"))

    return test_results


def test_imports():
    results = run_import_checks()
    failures = [(name, status) for name, status in results if status != "PASS"]
    assert not failures, failures


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ECS CHATBOT - IMPORT VERIFICATION TEST")
    print("=" * 80)

    results = run_import_checks()

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)

    for test_name, status in results:
        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {status}")

    print(f"\n{'=' * 80}")
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 80)

    if passed == total:
        print("\n✓ ALL IMPORTS VERIFIED SUCCESSFULLY - SYSTEM READY")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} TESTS FAILED - SYSTEM NOT READY")
        sys.exit(1)
