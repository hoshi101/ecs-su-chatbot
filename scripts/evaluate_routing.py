#!/usr/bin/env python3
"""Run API-level routing regression checks against /chat/."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.api.main import app  # noqa: E402


def load_cases(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate chat routing decisions.")
    parser.add_argument(
        "--cases",
        default=str(PROJECT_ROOT / "tests" / "data" / "routing_benchmark_cases.json"),
        help="Path to routing benchmark cases JSON",
    )
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default="gpt-5.4-mini")
    args = parser.parse_args()

    app.state.limiter.enabled = False
    client = TestClient(app)
    cases = load_cases(Path(args.cases))

    failures = []
    for case in cases:
        response = client.post(
            "/chat/",
            json={
                "session_id": f"routing-benchmark-{case['id']}-{uuid.uuid4()}",
                "query": case["query"],
                "enable_web_search": True,
                "force_web_search": False,
                "similarity_threshold": 0.7,
                "llm_provider": args.provider,
                "llm_model": args.model,
            },
        )
        payload = response.json()
        first = (payload.get("trace_events") or [{}])[0]
        details = first.get("details", {}) if isinstance(first, dict) else {}
        actual_intent = details.get("precheck_intent")
        is_shortcut = str(first.get("description", "")).startswith("Shortcut response selected")
        actual_variant = details.get("shortcut_variant")

        case_failures = []
        if response.status_code != 200:
            case_failures.append(f"status={response.status_code}")
        if actual_intent != case["expected_intent"]:
            case_failures.append(f"intent expected={case['expected_intent']} actual={actual_intent}")
        if is_shortcut != case["expected_shortcut"]:
            case_failures.append(f"shortcut expected={case['expected_shortcut']} actual={is_shortcut}")
        expected_variant = case.get("expected_variant")
        if expected_variant and actual_variant != expected_variant:
            case_failures.append(f"variant expected={expected_variant} actual={actual_variant}")

        status_label = "PASS" if not case_failures else "FAIL"
        print(
            f"[{status_label}] {case['id']} {case['query']} | "
            f"intent={actual_intent} | shortcut={is_shortcut} | variant={actual_variant}"
        )
        if case_failures:
            failures.append({"id": case["id"], "query": case["query"], "errors": case_failures})

    print(f"\nSummary: {len(cases) - len(failures)}/{len(cases)} passed")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure['id']} {failure['query']}: {'; '.join(failure['errors'])}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
