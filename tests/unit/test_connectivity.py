#!/usr/bin/env python3
"""
Comprehensive connectivity and API testing script.
Tests all external services and API endpoints.
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_connectivity():
    """Test connectivity to all external services."""
    print("=" * 80)
    print("TESTING EXTERNAL SERVICE CONNECTIVITY")
    print("=" * 80)

    test_results = []

    # Test 1: Qdrant Connection and Collection
    print("\n[1/5] Testing Qdrant connection and collection...")
    try:
        from src.backend.services.vectorstore import _get_qdrant_client
        from src.backend.core.config import QDRANT_COLLECTION_NAME

        start = time.time()
        client = _get_qdrant_client()

        # Check collections
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        print(f"   ✓ Connected to Qdrant successfully ({(time.time() - start)*1000:.2f}ms)")
        print(f"   ✓ Available collections: {collection_names}")

        if QDRANT_COLLECTION_NAME in collection_names:
            collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
            print(f"   ✓ Collection '{QDRANT_COLLECTION_NAME}' exists")
            print(f"   ✓ Document count: {collection_info.points_count}")
            test_results.append(("Qdrant Connection", "PASS", f"{collection_info.points_count} documents"))
        else:
            print(f"   ⚠ Collection '{QDRANT_COLLECTION_NAME}' does not exist (will be created on first use)")
            test_results.append(("Qdrant Connection", "PASS", "No collection yet"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Qdrant Connection", "FAIL", str(e)))
        return test_results

    # Test 2: BGE-M3 Embedding Generation
    print("\n[2/5] Testing BGE-M3 embedding generation...")
    try:
        from src.backend.services.vectorstore import embeddings

        test_text = "This is a test query for the FSS Hero chatbot system"
        start = time.time()
        embedding = embeddings.embed_query(test_text)
        latency = (time.time() - start) * 1000

        print(f"   ✓ Generated embedding successfully ({latency:.2f}ms)")
        print(f"   ✓ Embedding dimensions: {len(embedding)}")
        print(f"   ✓ Embedding sample (first 5 values): {embedding[:5]}")

        assert len(embedding) == 1024, f"Expected 1024 dimensions, got {len(embedding)}"
        test_results.append(("BGE-M3 Embeddings", "PASS", f"{latency:.2f}ms"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("BGE-M3 Embeddings", "FAIL", str(e)))
        return test_results

    # Test 3: Google Gemini API
    print("\n[3/5] Testing Google Gemini API connectivity...")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        from src.backend.core.config import GOOGLE_API_KEY

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY
        )

        start = time.time()
        response = llm.invoke([HumanMessage(content="Respond with 'OK' only")])
        latency = (time.time() - start) * 1000

        print(f"   ✓ Connected to Gemini API successfully ({latency:.2f}ms)")
        print(f"   ✓ Model: gemini-2.5-flash")
        print(f"   ✓ Response: {response.content[:100]}")
        test_results.append(("Google Gemini API", "PASS", f"{latency:.2f}ms"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Google Gemini API", "FAIL", str(e)))
        return test_results

    # Test 4: Tavily Web Search
    print("\n[4/5] Testing Tavily web search...")
    try:
        from langchain_tavily import TavilySearch
        from src.backend.core.config import TAVILY_API_KEY, SEARCH_DOMAINS

        import os
        os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

        tavily = TavilySearch(
            max_results=1,
            topic="general",
            include_domains=SEARCH_DOMAINS
        )

        start = time.time()
        result = tavily.invoke({"query": "test"})
        latency = (time.time() - start) * 1000

        print(f"   ✓ Connected to Tavily API successfully ({latency:.2f}ms)")
        print(f"   ✓ Search domains: {SEARCH_DOMAINS}")
        print(f"   ✓ Result type: {type(result)}")
        test_results.append(("Tavily Web Search", "PASS", f"{latency:.2f}ms"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Tavily Web Search", "FAIL", str(e)))

    # Test 5: Query Enhancement
    print("\n[5/5] Testing HERO Bot query enhancement...")
    try:
        from src.backend.core.agent import enhance_query_hero_bot_style

        test_query = "How to set stop loss?"
        start = time.time()
        enhanced = enhance_query_hero_bot_style(test_query)
        latency = (time.time() - start) * 1000

        print(f"   ✓ Query enhancement working ({latency:.2f}ms)")
        print(f"   ✓ Original: {test_query}")
        print(f"   ✓ Enhanced: {enhanced}")
        test_results.append(("Query Enhancement", "PASS", f"{latency:.2f}ms"))
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        test_results.append(("Query Enhancement", "FAIL", str(e)))

    return test_results


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("FSS HERO CHATBOT - CONNECTIVITY VERIFICATION TEST")
    print("=" * 80)

    results = test_connectivity()

    print("\n" + "=" * 80)
    print("CONNECTIVITY TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, status, _ in results if status == "PASS")
    total = len(results)

    for test_name, status, details in results:
        status_symbol = "✓" if status == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {status} ({details})")

    print(f"\n{'=' * 80}")
    print(f"RESULTS: {passed}/{total} connectivity tests passed")
    print("=" * 80)

    if passed == total:
        print("\n✓ ALL CONNECTIVITY TESTS PASSED - SERVICES READY")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} TESTS FAILED - SERVICES NOT READY")
        sys.exit(1)
