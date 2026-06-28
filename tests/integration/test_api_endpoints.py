#!/usr/bin/env python3
"""
Test script for ECS chatbot API endpoints.
Tests the three new testing and monitoring endpoints:
1. /debug/retrieval-test - Test RAG retrieval
2. /health/detailed - Comprehensive health check
3. /debug/embedding-test - Test embeddings and similarity
"""

import requests
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# API base URL (adjust if needed)
BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8001").rstrip("/")


def print_response(title: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2))
    print(f"{'='*80}\n")


def test_retrieval(query: str = "เบอร์ติดต่อภาควิชาวิศวกรรมไฟฟ้าคืออะไร", threshold: float = 0.7, top_k: int = 5):
    """
    Test the retrieval endpoint with a sample query

    This tests:
    - Query enhancement (if enabled)
    - Similarity search with configurable threshold
    - Retrieval latency measurement
    - Collection statistics
    """
    print(f"\n🔍 Testing Retrieval Endpoint")
    print(f"Query: '{query}'")
    print(f"Threshold: {threshold}, Top-K: {top_k}")

    url = f"{BASE_URL}/debug/retrieval-test"
    payload = {
        "query": query,
        "similarity_threshold": threshold,
        "top_k": top_k,
        "return_scores": True,
        "return_metadata": True
    }

    try:
        response = requests.post(url, json=payload)
        print_response("Retrieval Test Results", response)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {data['total_results']} results in {data['retrieval_latency_ms']:.2f}ms")

            if data.get('enhanced_query'):
                print(f"✓ Query enhanced: '{data['original_query']}' → '{data['enhanced_query']}'")

            if data['results']:
                print(f"\nTop result preview:")
                top_result = data['results'][0]
                print(f"  Score: {top_result.get('score', 'N/A')}")
                print(f"  Content: {top_result['content'][:200]}...")

        return response

    except Exception as e:
        print(f"❌ Error testing retrieval: {e}")
        return None


def test_detailed_health():
    """
    Test the detailed health check endpoint

    This checks:
    - Qdrant connection and collection status
    - BGE-M3 embedding generation
    - Google Gemini API connectivity
    - Tavily web search (if configured)
    - DocumentProcessor initialization
    """
    print(f"\n🏥 Testing Detailed Health Check Endpoint")

    url = f"{BASE_URL}/health/detailed"

    try:
        response = requests.get(url)
        print_response("Detailed Health Check Results", response)

        if response.status_code == 200:
            data = response.json()
            overall = data['overall_status']
            summary = data['summary']

            print(f"\n{'='*80}")
            print(f"Overall Status: {overall.upper()}")
            print(f"{'='*80}")
            print(f"Total Components: {summary['total_components']}")
            print(f"  ✓ Healthy: {summary['healthy']}")
            print(f"  ⚠ Degraded: {summary['degraded']}")
            print(f"  ✗ Unhealthy: {summary['unhealthy']}")
            print(f"{'='*80}")

            print(f"\nComponent Details:")
            for component in data['components']:
                status_symbol = {
                    'healthy': '✓',
                    'degraded': '⚠',
                    'unhealthy': '✗'
                }.get(component['status'], '?')

                print(f"\n{status_symbol} {component['name']}: {component['status'].upper()}")
                if component.get('latency_ms'):
                    print(f"  Latency: {component['latency_ms']}ms")
                if component.get('details'):
                    print(f"  Details: {component['details']}")
                if component.get('error'):
                    print(f"  Error: {component['error']}")

        return response

    except Exception as e:
        print(f"❌ Error testing health check: {e}")
        return None


def test_embeddings_basic():
    """
    Test basic embedding generation

    This tests:
    - Embedding generation for multiple texts
    - Similarity matrix computation
    - Embedding dimensions
    """
    print(f"\n🧮 Testing Embedding Endpoint (Basic)")

    url = f"{BASE_URL}/debug/embedding-test"
    payload = {
        "texts": [
            "หลักสูตรวิศวกรรมไฟฟ้าและระบบคอมพิวเตอร์",
            "ข้อมูลติดต่อภาควิชาวิศวกรรมไฟฟ้า",
            "รายชื่ออาจารย์ประจำภาควิชา"
        ],
        "compute_similarities": True
    }

    try:
        response = requests.post(url, json=payload)
        print_response("Embedding Test Results (Basic)", response)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Generated embeddings for {data['total_texts']} texts in {data['processing_time_ms']:.2f}ms")
            print(f"✓ Model: {data['embedding_model']}")

            if data['results']:
                print(f"\nEmbedding dimensions: {data['results'][0]['embedding_dimensions']}")

            if data.get('similarity_matrix'):
                print(f"\nSimilarity Matrix:")
                for i, row in enumerate(data['similarity_matrix']):
                    print(f"  Text {i+1}: {[f'{s:.3f}' for s in row]}")

        return response

    except Exception as e:
        print(f"❌ Error testing embeddings: {e}")
        return None


def test_embeddings_with_reference():
    """
    Test embedding generation with reference text comparison

    This tests:
    - Embedding generation
    - Similarity computation against reference
    """
    print(f"\n🧮 Testing Embedding Endpoint (With Reference)")

    url = f"{BASE_URL}/debug/embedding-test"
    payload = {
        "texts": [
            "ข้อมูลหลักสูตรระดับปริญญาตรี",
            "ข้อมูลติดต่อภาควิชา",
            "งานวิจัยของอาจารย์"
        ],
        "reference_text": "อยากทราบข้อมูลหลักสูตรของภาควิชาวิศวกรรมไฟฟ้า",
        "compute_similarities": False
    }

    try:
        response = requests.post(url, json=payload)
        print_response("Embedding Test Results (With Reference)", response)

        if response.status_code == 200:
            data = response.json()
            print(f"\nReference Text: '{payload['reference_text']}'")
            print(f"\nSimilarities to Reference:")
            for result in data['results']:
                similarity = result.get('similarity_to_reference')
                if similarity is not None:
                    print(f"  {result['text_preview']}: {similarity:.3f}")

        return response

    except Exception as e:
        print(f"❌ Error testing embeddings with reference: {e}")
        return None


def run_all_tests():
    """Run all endpoint tests"""
    print(f"\n{'#'*80}")
    print(f"# ECS Chatbot API - Testing and Monitoring Endpoints")
    print(f"# Base URL: {BASE_URL}")
    print(f"{'#'*80}")

    # Test 1: Detailed Health Check (run first to verify system is operational)
    test_detailed_health()

    # Test 2: Retrieval Test (with default parameters)
    test_retrieval()

    # Test 3: Retrieval Test (with different threshold)
    test_retrieval(
        query="หลักสูตร ECS เรียนเกี่ยวกับอะไร",
        threshold=0.5,
        top_k=3
    )

    # Test 4: Basic Embedding Test
    test_embeddings_basic()

    # Test 5: Embedding Test with Reference
    test_embeddings_with_reference()

    print(f"\n{'#'*80}")
    print(f"# All tests completed!")
    print(f"{'#'*80}\n")


if __name__ == "__main__":
    # You can run all tests or individual tests
    import sys

    if len(sys.argv) > 1:
        test_name = sys.argv[1]

        if test_name == "health":
            test_detailed_health()
        elif test_name == "retrieval":
            test_retrieval()
        elif test_name == "embeddings":
            test_embeddings_basic()
        elif test_name == "embeddings-ref":
            test_embeddings_with_reference()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: health, retrieval, embeddings, embeddings-ref")
    else:
        # Run all tests
        run_all_tests()
