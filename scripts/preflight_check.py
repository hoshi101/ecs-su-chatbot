#!/usr/bin/env python3
"""
Run a lightweight preflight check against the local ECS chatbot backend.
"""

import argparse
import sys
from typing import Any, Dict

import requests


def check(name: str, condition: bool, details: str) -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}: {details}")
    return condition


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local preflight checks for the ECS chatbot backend.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8001", help="Backend base URL")
    parser.add_argument(
        "--query",
        default="เบอร์ติดต่อภาควิชาวิศวกรรมไฟฟ้าคืออะไร",
        help="Representative test query",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    ok = True

    try:
        health = requests.get(f"{base_url}/health", timeout=10)
        ok &= check("Health", health.ok and health.json().get("status") == "ok", health.text)
    except Exception as exc:
        check("Health", False, str(exc))
        return 1

    try:
        detailed = requests.get(f"{base_url}/health/detailed", timeout=60)
        detailed_json: Dict[str, Any] = detailed.json()
        component_names = [component["name"] for component in detailed_json.get("components", [])]
        ok &= check(
            "Detailed health",
            detailed.ok and detailed_json.get("overall_status") in {"healthy", "degraded"},
            f"overall_status={detailed_json.get('overall_status')} | components={component_names}",
        )
    except Exception as exc:
        check("Detailed health", False, str(exc))
        ok = False

    try:
        retrieval = requests.post(
            f"{base_url}/debug/retrieval-test",
            json={"query": args.query, "top_k": 3, "similarity_threshold": 0.7},
            timeout=60,
        )
        retrieval_json = retrieval.json()
        ok &= check(
            "Retrieval test",
            retrieval.ok and retrieval_json.get("total_results", 0) > 0,
            f"total_results={retrieval_json.get('total_results')} | enhanced_query={retrieval_json.get('enhanced_query')}",
        )
    except Exception as exc:
        check("Retrieval test", False, str(exc))
        ok = False

    try:
        chat = requests.post(
            f"{base_url}/chat/",
            json={
                "session_id": "preflight-check",
                "query": args.query,
                "enable_web_search": True,
                "force_web_search": False,
                "similarity_threshold": 0.7,
            },
            timeout=120,
        )
        chat_json = chat.json()
        trace_events = chat_json.get("trace_events", [])
        sources = chat_json.get("sources", [])
        ok &= check(
            "Chat response",
            chat.ok and bool(chat_json.get("response")),
            f"response_length={len(chat_json.get('response', ''))}",
        )
        ok &= check(
            "Workflow trace",
            len(trace_events) > 0,
            f"trace_events={len(trace_events)}",
        )
        ok &= check(
            "Source attribution",
            len(sources) > 0,
            f"sources={len(sources)}",
        )
    except Exception as exc:
        check("Chat response", False, str(exc))
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
