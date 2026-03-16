#!/usr/bin/env python3
import requests
import time
import json

API_BASE = "http://localhost:8000"

# Diverse test queries - platform-related only
queries = [
    ("ใช้ stop loss ยังไง", "order_management"),
    ("วิธีเปิดบัญชี", "account"),
    ("Moving Average คืออะไร", "technical_analysis"),
    ("HERO Strong Trend", "features"),
    ("Volume by Price", "features"),
]

results = []
total_time = 0
success_count = 0

print("=" * 70)
print("FINAL EVALUATION - FSS HERO CHATBOT")
print("=" * 70)
print(f"Testing {len(queries)} queries...\n")

for i, (query, category) in enumerate(queries, 1):
    print(f"[{i}/{len(queries)}] {query}")
    start = time.time()

    try:
        resp = requests.post(
            f"{API_BASE}/chat/",
            json={
                "session_id": f"test-{i}",
                "query": query,
                "enable_web_search": True,
                "similarity_threshold": 0.7
            },
            timeout=60
        )
        elapsed = time.time() - start

        if resp.status_code == 200:
            data = resp.json()

            # Extract info from trace
            route = "unknown"
            enhanced = query  # fallback

            for event in data.get("trace_events", []):
                if event.get("event_type") == "hero_bot_routing":
                    details = event.get("details", {})
                    route = details.get("decision", "unknown")
                    enhanced = details.get("enhanced_query", query)

            success_count += 1
            total_time += elapsed

            print(f"  ✓ Success in {elapsed:.1f}s")
            print(f"  Route: {route}")
            print(f"  Enhanced: {enhanced[:80]}...")
            print(f"  Response: {data['response'][:100]}...")

            results.append({
                "query": query,
                "category": category,
                "success": True,
                "response_time": round(elapsed, 2),
                "route": route,
                "enhanced_query": enhanced
            })
        else:
            print(f"  ✗ HTTP {resp.status_code}")
            print(f"  Time: {elapsed:.1f}s")
            results.append({
                "query": query,
                "category": category,
                "success": False,
                "error": f"HTTP {resp.status_code}",
                "response_time": round(elapsed, 2)
            })

    except Exception as e:
        elapsed = time.time() - start
        print(f"  ✗ Error: {str(e)[:50]}")
        print(f"  Time: {elapsed:.1f}s")
        results.append({
            "query": query,
            "category": category,
            "success": False,
            "error": str(e)[:100],
            "response_time": round(elapsed, 2)
        })

    print()

# Calculate metrics
avg_time = total_time / success_count if success_count > 0 else 0
success_rate = (success_count / len(queries)) * 100

print("=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)
print(f"Total Queries: {len(queries)}")
print(f"Successful: {success_count}/{len(queries)} ({success_rate:.1f}%)")
print(f"Average Response Time: {avg_time:.2f} seconds")
print(f"Fastest: {min([r['response_time'] for r in results if r['success']], default=0):.2f}s")
print(f"Slowest: {max([r['response_time'] for r in results if r['success']], default=0):.2f}s")
print("=" * 70)

# Save results
output = {
    "summary": {
        "total": len(queries),
        "successful": success_count,
        "success_rate": round(success_rate, 1),
        "avg_response_time": round(avg_time, 2)
    },
    "results": results
}

with open("final_evaluation.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n✓ Results saved to: final_evaluation.json")
