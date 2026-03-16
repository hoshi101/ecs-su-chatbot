#!/usr/bin/env python3
"""
Test script to evaluate the FSS HERO Chatbot performance
Measures: Response Time, Accuracy, Query Enhancement Impact, Routing Accuracy
"""

import requests
import time
import json
from typing import Dict, List, Tuple

API_BASE = "http://localhost:8000"

# Test queries covering different aspects of the platform
TEST_QUERIES = [
    {
        "query": "ใช้ stop loss ยังไง",
        "expected_route": "rag",
        "category": "order_management"
    },
    {
        "query": "HERO Strong Trend คืออะไร",
        "expected_route": "rag",
        "category": "features"
    },
    {
        "query": "วิธีเปิดบัญชีซื้อขาย",
        "expected_route": "rag",
        "category": "account"
    },
    {
        "query": "Moving Average 200 วัน",
        "expected_route": "rag",
        "category": "technical_analysis"
    },
    {
        "query": "How to use backtest feature",
        "expected_route": "rag",
        "category": "features"
    },
    {
        "query": "Volume by Price คำนวณยังไง",
        "expected_route": "rag",
        "category": "features"
    },
    {
        "query": "ราคาหุ้น AAPL วันนี้",
        "expected_route": "web",
        "category": "out_of_scope"
    },
    {
        "query": "what is python",
        "expected_route": "end",
        "category": "out_of_scope"
    }
]


def test_single_query(query: str, enable_web_search: bool = True,
                      enable_query_enhancement: bool = True) -> Dict:
    """Test a single query and measure metrics"""

    start_time = time.time()

    payload = {
        "session_id": "test-session",
        "query": query,
        "enable_web_search": enable_web_search,
        "similarity_threshold": 0.7
    }

    try:
        response = requests.post(
            f"{API_BASE}/chat/",
            json=payload,
            timeout=30
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()

            # Extract routing info from trace events
            route_taken = None
            enhanced_query = None

            for event in data.get("trace_events", []):
                if event.get("event_type") == "hero_bot_routing":
                    route_taken = event.get("details", {}).get("router_decision")
                    enhanced_query = event.get("details", {}).get("enhanced_query")

            return {
                "success": True,
                "response": data.get("response", ""),
                "response_time": round(elapsed, 2),
                "route_taken": route_taken,
                "enhanced_query": enhanced_query,
                "trace_events": len(data.get("trace_events", []))
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response_time": round(elapsed, 2)
            }

    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "response_time": round(elapsed, 2)
        }


def evaluate_system():
    """Run full system evaluation"""

    print("=" * 80)
    print("FSS HERO CHATBOT EVALUATION")
    print("=" * 80)
    print()

    results = []
    total_response_time = 0
    successful_queries = 0
    routing_correct = 0

    print(f"Testing {len(TEST_QUERIES)} queries...\n")

    for i, test_case in enumerate(TEST_QUERIES, 1):
        query = test_case["query"]
        expected_route = test_case["expected_route"]
        category = test_case["category"]

        print(f"[{i}/{len(TEST_QUERIES)}] Testing: {query[:50]}...")

        result = test_single_query(query)

        if result["success"]:
            successful_queries += 1
            total_response_time += result["response_time"]

            # Check routing accuracy
            if result["route_taken"] == expected_route:
                routing_correct += 1
                routing_status = "✓"
            else:
                routing_status = f"✗ (expected: {expected_route}, got: {result['route_taken']})"

            print(f"  ✓ Success in {result['response_time']}s | Route: {routing_status}")
            print(f"  Enhanced: {result['enhanced_query'][:80] if result['enhanced_query'] else 'N/A'}...")
            print()

            results.append({
                "query": query,
                "category": category,
                "expected_route": expected_route,
                "actual_route": result["route_taken"],
                "response_time": result["response_time"],
                "enhanced_query": result["enhanced_query"],
                "response_preview": result["response"][:200]
            })
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
            print()

    # Calculate metrics
    avg_response_time = total_response_time / successful_queries if successful_queries > 0 else 0
    success_rate = (successful_queries / len(TEST_QUERIES)) * 100
    routing_accuracy = (routing_correct / successful_queries) * 100 if successful_queries > 0 else 0

    # Print summary
    print("=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Queries: {len(TEST_QUERIES)}")
    print(f"Successful: {successful_queries} ({success_rate:.1f}%)")
    print(f"Failed: {len(TEST_QUERIES) - successful_queries}")
    print(f"Average Response Time: {avg_response_time:.2f} seconds")
    print(f"Routing Accuracy: {routing_correct}/{successful_queries} ({routing_accuracy:.1f}%)")
    print()

    # Query Enhancement Impact (compare with/without)
    print("=" * 80)
    print("QUERY ENHANCEMENT IMPACT")
    print("=" * 80)

    sample_query = "ใช้ stop loss ยังไง"
    print(f"Sample Query: {sample_query}\n")

    # Test without enhancement (will still route, but won't reformulate)
    result_enhanced = test_single_query(sample_query, enable_query_enhancement=True)

    if result_enhanced["success"]:
        print(f"Enhanced Query: {result_enhanced['enhanced_query']}")
        print(f"Response Time: {result_enhanced['response_time']}s")
        print()

    # Save detailed results
    with open("/home/hoshi/hoshi/demo-section/fsshero-chatbot/evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_queries": len(TEST_QUERIES),
                "successful_queries": successful_queries,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(avg_response_time, 2),
                "routing_accuracy": round(routing_accuracy, 2)
            },
            "detailed_results": results
        }, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print("Detailed results saved to: evaluation_results.json")
    print("=" * 80)

    return {
        "success_rate": success_rate,
        "avg_response_time": avg_response_time,
        "routing_accuracy": routing_accuracy
    }


if __name__ == "__main__":
    metrics = evaluate_system()
