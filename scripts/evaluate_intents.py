#!/usr/bin/env python3

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.core.agent import get_default_llm_settings, resolve_precheck_decision


def main() -> None:
    cases_path = PROJECT_ROOT / "tests" / "data" / "intent_eval_cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    defaults = get_default_llm_settings()

    passed = 0
    for case in cases:
        intent, reason, variant, source = resolve_precheck_decision(
            case["query"],
            defaults["provider"],
            defaults["model"],
        )
        ok = intent == case["expected_intent"] and variant == case["expected_variant"]
        status = "PASS" if ok else "FAIL"
        print(
            f"{status} | query={case['query']} | intent={intent} | variant={variant} | source={source} | reason={reason}"
        )
        if ok:
            passed += 1

    print(f"\nSummary: {passed}/{len(cases)} passed")


if __name__ == "__main__":
    main()
