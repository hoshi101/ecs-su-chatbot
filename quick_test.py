#!/usr/bin/env python3
import requests
import time
import json

API_BASE = "http://localhost:8000"

queries = [
    "ใช้ stop loss ยังไง",
    "HERO Strong Trend คืออะไร",
    "Moving Average 200 วัน"
]

print("Testing 3 queries...\n")

for i, query in enumerate(queries, 1):
    print(f"[{i}/3] {query}")
    start = time.time()

    try:
        resp = requests.post(
            f"{API_BASE}/chat/",
            json={"session_id": "test", "query": query, "enable_web_search": False},
            timeout=90
        )
        elapsed = time.time() - start

        if resp.status_code == 200:
            data = resp.json()
            route = "unknown"
            for event in data.get("trace_events", []):
                if event.get("event_type") == "hero_bot_routing":
                    route = event.get("details", {}).get("decision", "unknown")

            print(f"✓ {elapsed:.1f}s | Route: {route}")
            print(f"  Response: {data['response'][:150]}...")
        else:
            print(f"✗ HTTP {resp.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print()
