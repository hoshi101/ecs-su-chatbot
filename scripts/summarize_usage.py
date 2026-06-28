import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean


def load_events(path: Path) -> list[dict]:
    if not path.exists():
        return []

    events = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def percent(value: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{(value / total) * 100:.1f}%"


def print_counter(title: str, counter: Counter, total: int) -> None:
    print(f"\n{title}")
    if not counter:
        print("- none")
        return
    for key, count in counter.most_common():
        print(f"- {key or 'unknown'}: {count} ({percent(count, total)})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize chat usage events for demo/reporting.")
    parser.add_argument(
        "--file",
        default="logs/usage_events.jsonl",
        help="Path to usage_events.jsonl",
    )
    parser.add_argument(
        "--latest",
        type=int,
        default=10,
        help="Number of latest query previews to show",
    )
    args = parser.parse_args()

    path = Path(args.file)
    events = load_events(path)
    total = len(events)

    print(f"Usage file: {path}")
    print(f"Total chat requests: {total}")

    if not events:
        return 0

    latencies = [event.get("latency_ms") for event in events if isinstance(event.get("latency_ms"), (int, float))]
    source_counts = [event.get("source_count") for event in events if isinstance(event.get("source_count"), int)]

    print(f"Success: {sum(1 for event in events if event.get('status') == 'success')}")
    print(f"Errors: {sum(1 for event in events if event.get('status') == 'error')}")
    if latencies:
        print(f"Average latency: {mean(latencies):.2f} ms")
        print(f"Max latency: {max(latencies):.2f} ms")
    if source_counts:
        print(f"Average source count: {mean(source_counts):.2f}")

    print_counter("Routes", Counter(event.get("route") for event in events), total)
    print_counter("Precheck intents", Counter(event.get("precheck_intent") for event in events), total)
    print_counter("Models", Counter(f"{event.get('llm_provider')}/{event.get('llm_model')}" for event in events), total)

    print("\nLatest queries")
    for event in events[-args.latest :]:
        print(f"- [{event.get('status')}] {event.get('query_preview')} ({event.get('latency_ms')} ms)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
