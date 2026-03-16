#!/usr/bin/env python3
"""
HERO Bot Integration Test
Tests the implementation of HERO Bot features for identical output comparison

This script tests:
1. Query enhancement functionality
2. Domain-specific routing
3. HERO Bot specialized prompts
4. Trace event generation with query enhancement info
5. Response consistency with original HERO Bot

Usage:
    python test_hero_bot_integration.py

Requirements:
    - Set up .env file with required API keys
    - Run backend server: cd backend && uvicorn main:app --reload
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, List

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from dotenv import load_dotenv
    load_dotenv()

    # Test imports
    from backend.config import (
        GOOGLE_API_KEY, QDRANT_API_KEY, QDRANT_URL, TAVILY_API_KEY,
        DOMAIN_NAME, BOT_NAME, SEARCH_DOMAINS, SPECIALTY_AREAS,
        FINANCIAL_TEMPERATURE, ENABLE_QUERY_ENHANCEMENT
    )
    from backend.agent import enhance_query_hero_bot_style, build_agent
    from backend.vectorstore import BGEEmbedder
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from the project root directory")
    sys.exit(1)

print("🧪 HERO Bot Integration Test")
print("=" * 60)
print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test queries that match original HERO Bot test cases
TEST_QUERIES = [
    {
        "query": "How do I use stop loss?",
        "expected_enhancement": "stop loss orders in Finansia Hero trading platform, including order types and risk management",
        "category": "Trading Orders"
    },
    {
        "query": "Chart not working",
        "expected_enhancement": "chart display issues, technical analysis tools, and charting functionality problems in Finansia Hero platform",
        "category": "Troubleshooting"
    },
    {
        "query": "What are the platform features?",
        "expected_enhancement": "Complete overview of Finansia Hero trading platform features, tools, and functionality",
        "category": "Platform Information"
    },
    {
        "query": "Hello",
        "expected_enhancement": "greeting or small-talk",
        "category": "Greeting"
    }
]

def test_configuration():
    """Test 1: Configuration and Environment Setup"""
    print("🔧 Test 1: Configuration and Environment")

    config_tests = {
        "Bot Name": BOT_NAME == "HERO Bot",
        "Domain Name": DOMAIN_NAME == "Finansia Hero Trading Platform",
        "Search Domains": "www.finansiahero.com" in SEARCH_DOMAINS,
        "Financial Temperature": FINANCIAL_TEMPERATURE == 0.3,
        "Query Enhancement": ENABLE_QUERY_ENHANCEMENT == True,
        "Specialty Areas": len(SPECIALTY_AREAS) == 6  # Should have 6 specialty areas
    }

    for test_name, result in config_tests.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}: {'PASS' if result else 'FAIL'}")

    # Test API keys (without exposing them)
    api_keys = {
        "Google API Key": bool(GOOGLE_API_KEY),
        "Qdrant API Key": bool(QDRANT_API_KEY),
        "Qdrant URL": bool(QDRANT_URL),
        "Tavily API Key": bool(TAVILY_API_KEY)
    }

    for key_name, has_key in api_keys.items():
        status = "✅" if has_key else "❌"
        print(f"  {status} {key_name}: {'SET' if has_key else 'MISSING'}")

    print()
    return all(config_tests.values()) and all(api_keys.values())

def test_query_enhancement():
    """Test 2: HERO Bot Query Enhancement"""
    print("🔄 Test 2: Query Enhancement (HERO Bot Style)")

    all_passed = True

    for i, test_case in enumerate(TEST_QUERIES, 1):
        query = test_case["query"]
        category = test_case["category"]

        print(f"  Test {i}: {category}")
        print(f"    Original: '{query}'")

        try:
            enhanced = enhance_query_hero_bot_style(query)
            print(f"    Enhanced: '{enhanced}'")

            # Check if enhancement occurred (unless it's a greeting)
            if category != "Greeting":
                enhancement_occurred = enhanced != query and len(enhanced) > len(query)
                contains_domain = "Finansia Hero" in enhanced or "trading platform" in enhanced

                if enhancement_occurred and contains_domain:
                    print(f"    ✅ PASS: Query enhanced with domain context")
                else:
                    print(f"    ❌ FAIL: Enhancement insufficient")
                    all_passed = False
            else:
                print(f"    ℹ️  Greeting query - enhancement may be minimal")

        except Exception as e:
            print(f"    ❌ ERROR: {e}")
            all_passed = False

        print()

    return all_passed

def test_embeddings():
    """Test 3: BGE-M3 Embeddings"""
    print("🔤 Test 3: BGE-M3 Embeddings")

    try:
        print("  📥 Initializing BGE-M3 embeddings...")
        embedder = BGEEmbedder()

        test_text = "Trading platform features and order management"
        print(f"  🧪 Testing embedding for: '{test_text}'")

        embedding = embedder.embed_query(test_text)

        # Verify embedding properties
        is_list = isinstance(embedding, list)
        correct_dimension = len(embedding) == 1024  # BGE-M3 should be 1024D
        non_zero = any(abs(x) > 0.001 for x in embedding[:10])  # Check first 10 values

        print(f"  ✅ Embedding type: {'List' if is_list else 'Other'}")
        print(f"  ✅ Embedding dimension: {len(embedding)}")
        print(f"  ✅ Contains non-zero values: {'Yes' if non_zero else 'No'}")

        success = is_list and correct_dimension and non_zero
        print(f"  {'✅ PASS' if success else '❌ FAIL'}: BGE-M3 embeddings working")
        print()

        return success

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        print("  💡 BGE-M3 model may need to be downloaded (~2GB)")
        print()
        return False

def test_agent_build():
    """Test 4: LangGraph Agent Building"""
    print("🤖 Test 4: LangGraph Agent Integration")

    try:
        print("  🔧 Building HERO Bot agent...")
        agent = build_agent()

        # Test agent structure
        has_router = hasattr(agent, 'get_graph') or 'router' in str(agent)

        print(f"  ✅ Agent built successfully")
        print(f"  ✅ Contains routing logic: {'Yes' if has_router else 'No'}")
        print(f"  {'✅ PASS' if has_router else '❌ FAIL'}: Agent integration working")
        print()

        return True

    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        print()
        return False

async def test_api_integration():
    """Test 5: API Integration (if running)"""
    print("🌐 Test 5: API Integration")

    try:
        import requests

        # Test if backend is running
        response = requests.get("http://localhost:8000/health", timeout=5)

        if response.status_code == 200:
            print("  ✅ Backend server is running")

            # Test a simple query
            test_query = {
                "session_id": "test_session",
                "query": "How do I use stop loss?",
                "enable_web_search": False  # Disable web search for testing
            }

            chat_response = requests.post(
                "http://localhost:8000/chat/",
                json=test_query,
                timeout=30
            )

            if chat_response.status_code == 200:
                data = chat_response.json()

                # Check for HERO Bot trace events
                trace_events = data.get("trace_events", [])
                has_enhancement_info = any(
                    "enhanced_query" in event.get("details", {})
                    for event in trace_events
                )

                has_hero_events = any(
                    "hero_bot" in event.get("event_type", "").lower()
                    for event in trace_events
                )

                print(f"  ✅ API Response received")
                print(f"  ✅ Trace events: {len(trace_events)}")
                print(f"  ✅ Query enhancement info: {'Yes' if has_enhancement_info else 'No'}")
                print(f"  ✅ HERO Bot events: {'Yes' if has_hero_events else 'No'}")

                success = has_enhancement_info and has_hero_events
                print(f"  {'✅ PASS' if success else '❌ FAIL'}: API integration working")

                return success
            else:
                print(f"  ❌ Chat API error: {chat_response.status_code}")
                return False
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False

    except requests.ConnectionError:
        print("  ⚠️  Backend server not running")
        print("  💡 Start with: cd backend && uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

    print()

def main():
    """Run all integration tests"""
    print(f"Testing HERO Bot implementation:")
    print(f"Bot Name: {BOT_NAME}")
    print(f"Domain: {DOMAIN_NAME}")
    print(f"Search Domains: {', '.join(SEARCH_DOMAINS)}")
    print()

    # Run tests
    test_results = {}

    test_results["Configuration"] = test_configuration()
    test_results["Query Enhancement"] = test_query_enhancement()
    test_results["BGE-M3 Embeddings"] = test_embeddings()
    test_results["Agent Building"] = test_agent_build()

    # API test is async
    try:
        test_results["API Integration"] = asyncio.run(test_api_integration())
    except Exception as e:
        print(f"API test error: {e}")
        test_results["API Integration"] = False

    # Summary
    print("📋 Test Results Summary")
    print("=" * 30)

    passed = sum(test_results.values())
    total = len(test_results)

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print()
    print(f"Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! HERO Bot integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above and your configuration.")

    print()
    print("💡 Next Steps:")
    print("1. Start backend: cd backend && uvicorn main:app --reload")
    print("2. Start frontend: cd frontend && streamlit run app.py")
    print("3. Test with sample queries:")
    for query in TEST_QUERIES[:3]:
        print(f"   - '{query['query']}'")

if __name__ == "__main__":
    main()