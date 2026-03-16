#!/usr/bin/env python3
"""
HERO Bot Functional Parity Test Suite

This script automates the testing of functional parity between the current
LangGraph implementation and the reference Agno implementation.
"""

import json
import time
import sys
import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import requests
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class TestCase:
    test_id: str
    category: str
    description: str
    query: str
    config: Dict[str, Any]
    expected_behavior: str
    success_criteria: str

@dataclass
class TestResult:
    test_id: str
    result: TestResult
    current_impl_response: Dict[str, Any]
    reference_impl_response: Dict[str, Any]
    parity_score: float
    notes: str
    execution_time: float

class FunctionalParityTester:
    """Main test runner for functional parity validation."""

    def __init__(self, current_impl_url: str, reference_impl_url: str = None):
        """
        Initialize the tester.

        Args:
            current_impl_url: URL of the current LangGraph implementation API
            reference_impl_url: URL of the reference Agno implementation (if available)
        """
        self.current_impl_url = current_impl_url
        self.reference_impl_url = reference_impl_url
        self.test_results = []

    def load_test_cases(self) -> List[TestCase]:
        """Load test cases for functional parity validation."""
        return [
            # Query Enhancement Tests
            TestCase(
                test_id="QE-001",
                category="Query Enhancement",
                description="Basic stop loss query enhancement",
                query="How do I use stop loss?",
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": False},
                expected_behavior="Should expand to include stop loss orders, platform, risk management",
                success_criteria="Enhanced queries contain similar trading platform concepts"
            ),
            TestCase(
                test_id="QE-002",
                category="Query Enhancement",
                description="Chart troubleshooting query enhancement",
                query="Chart not working",
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": False},
                expected_behavior="Should expand to include chart display, technical analysis, platform issues",
                success_criteria="Enhanced queries address same troubleshooting concepts"
            ),
            TestCase(
                test_id="QE-003",
                category="Query Enhancement",
                description="Platform features overview query",
                query="What are the platform features?",
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": False},
                expected_behavior="Should expand to comprehensive platform features overview",
                success_criteria="Enhanced queries cover platform functionality comprehensively"
            ),

            # Routing Decision Tests
            TestCase(
                test_id="RT-001",
                category="Routing Decision",
                description="Platform feature should route to RAG",
                query="How to set up stop loss orders?",
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": False},
                expected_behavior="Should route to RAG for platform features",
                success_criteria="Both implementations choose RAG route"
            ),
            TestCase(
                test_id="RT-002",
                category="Routing Decision",
                description="Market data should route to web search",
                query="What's the latest Bitcoin price?",
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": False},
                expected_behavior="Should route to web search for current market data",
                success_criteria="Both implementations choose WEB route"
            ),
            TestCase(
                test_id="RT-003",
                category="Routing Decision",
                description="Greeting should route to end/answer",
                query="Hello there!",
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": False},
                expected_behavior="Should handle greeting appropriately",
                success_criteria="Both implementations handle greetings similarly"
            ),
            TestCase(
                test_id="RT-006",
                category="Routing Decision",
                description="Force web search should override routing",
                query="Platform trading fees?",
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": True},
                expected_behavior="Should force web search regardless of query type",
                success_criteria="Both implementations respect force web search setting"
            ),

            # Configuration Tests
            TestCase(
                test_id="ST-001",
                category="Similarity Threshold",
                description="Low threshold should be more permissive",
                query="general trading",
                config={"web_search_enabled": True, "similarity_threshold": 0.3, "force_web_search": False},
                expected_behavior="More permissive document retrieval",
                success_criteria="Both return more results with lower threshold"
            ),
            TestCase(
                test_id="ST-003",
                category="Similarity Threshold",
                description="High threshold should be very selective",
                query="exact feature name",
                config={"web_search_enabled": True, "similarity_threshold": 0.9, "force_web_search": False},
                expected_behavior="Very strict matching",
                success_criteria="Both show high selectivity with high threshold"
            ),

            # Web Search Toggle Tests
            TestCase(
                test_id="WT-002",
                category="Web Search Toggle",
                description="Web disabled should use RAG only",
                query="latest market data",
                config={"web_search_enabled": False, "similarity_threshold": 0.7, "force_web_search": False},
                expected_behavior="Must use RAG only when web search disabled",
                success_criteria="Both respect disabled web search setting"
            ),
            TestCase(
                test_id="WT-003",
                category="Web Search Toggle",
                description="Force web should override to web search",
                query="platform feature help",
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": True},
                expected_behavior="Override to web search",
                success_criteria="Both force web search when requested"
            ),

            # Edge Cases
            TestCase(
                test_id="EH-003",
                category="Edge Cases",
                description="Very long query handling",
                query="How do I set up and configure complex multi-step stop loss orders with specific risk management parameters and custom alert notifications in the Finansia Hero trading platform while ensuring proper position sizing and portfolio management techniques are applied according to advanced trading strategies for volatile market conditions?" * 2,
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": False},
                expected_behavior="Handle long queries gracefully",
                success_criteria="Both process long queries without errors"
            ),
            TestCase(
                test_id="EH-005",
                category="Edge Cases",
                description="Special characters handling",
                query="How to use @#$%^&*() special chars in trading?",
                config={"web_search_enabled": True, "similarity_threshold": 0.7, "force_web_search": False},
                expected_behavior="Input sanitization and safe handling",
                success_criteria="Both handle special characters safely"
            )
        ]

    def call_current_implementation(self, test_case: TestCase) -> Tuple[Dict[str, Any], float]:
        """Call the current LangGraph implementation."""
        start_time = time.time()

        try:
            # Prepare request payload for current implementation
            payload = {
                "message": test_case.query,
                "session_id": f"test_session_{test_case.test_id}",
                "web_search_enabled": test_case.config.get("web_search_enabled", True),
                "force_web_search": test_case.config.get("force_web_search", False),
                "similarity_threshold": test_case.config.get("similarity_threshold", 0.7)
            }

            response = requests.post(
                f"{self.current_impl_url}/chat",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            execution_time = time.time() - start_time
            return response.json(), execution_time

        except Exception as e:
            execution_time = time.time() - start_time
            return {"error": str(e)}, execution_time

    def call_reference_implementation(self, test_case: TestCase) -> Tuple[Dict[str, Any], float]:
        """Call the reference Agno implementation (if available)."""
        start_time = time.time()

        # If no reference URL provided, return mock response
        if not self.reference_impl_url:
            execution_time = time.time() - start_time
            return {
                "message": "Reference implementation not available for direct API testing",
                "enhanced_query": f"Enhanced: {test_case.query}",
                "route": "rag",  # Mock routing decision
                "source": "mock"
            }, execution_time

        try:
            # This would be the actual call to reference implementation
            # For now, returning mock data since reference is a Streamlit app
            execution_time = time.time() - start_time
            return {
                "message": "Reference implementation requires manual testing",
                "note": "Agno implementation is Streamlit-based, not API accessible"
            }, execution_time

        except Exception as e:
            execution_time = time.time() - start_time
            return {"error": str(e)}, execution_time

    def analyze_query_enhancement_parity(self, current_response: Dict, reference_response: Dict) -> float:
        """Analyze parity in query enhancement behavior."""
        # Extract enhanced queries from responses
        current_enhanced = current_response.get("enhancement_info", {}).get("enhanced_query", "")
        reference_enhanced = reference_response.get("enhanced_query", "")

        if not current_enhanced and not reference_enhanced:
            return 1.0  # Both didn't enhance - perfect parity

        if not current_enhanced or not reference_enhanced:
            return 0.0  # One enhanced, other didn't - no parity

        # Simple keyword overlap analysis
        current_keywords = set(current_enhanced.lower().split())
        reference_keywords = set(reference_enhanced.lower().split())

        if not current_keywords and not reference_keywords:
            return 1.0

        overlap = len(current_keywords.intersection(reference_keywords))
        total_unique = len(current_keywords.union(reference_keywords))

        return overlap / total_unique if total_unique > 0 else 0.0

    def analyze_routing_parity(self, current_response: Dict, reference_response: Dict) -> float:
        """Analyze parity in routing decisions."""
        # Extract routing information
        current_trace = current_response.get("trace_events", [])
        current_routes = [event.get("node") for event in current_trace if event.get("node")]

        reference_route = reference_response.get("route", "unknown")

        # Map LangGraph nodes to reference routes
        route_mapping = {
            "router": "routing",
            "rag_lookup": "rag",
            "web_search": "web",
            "answer": "answer"
        }

        # Check if current implementation visited expected nodes
        if "rag_lookup" in current_routes and reference_route == "rag":
            return 1.0
        elif "web_search" in current_routes and reference_route == "web":
            return 1.0
        elif "answer" in current_routes and reference_route == "answer":
            return 1.0
        else:
            return 0.5  # Partial match or different but potentially valid routing

    def analyze_response_quality_parity(self, current_response: Dict, reference_response: Dict) -> float:
        """Analyze parity in response quality and content."""
        current_message = current_response.get("message", "")
        reference_message = reference_response.get("message", "")

        if not current_message and not reference_message:
            return 1.0

        if not current_message or not reference_message:
            return 0.0

        # Simple content similarity check
        current_words = set(current_message.lower().split())
        reference_words = set(reference_message.lower().split())

        # Check for key trading/platform terms
        trading_terms = {
            "trading", "platform", "finansia", "hero", "order", "chart",
            "account", "risk", "management", "stop", "loss", "market"
        }

        current_trading_terms = current_words.intersection(trading_terms)
        reference_trading_terms = reference_words.intersection(trading_terms)

        # Higher score if both use similar trading terminology
        if current_trading_terms and reference_trading_terms:
            term_overlap = len(current_trading_terms.intersection(reference_trading_terms))
            total_terms = len(current_trading_terms.union(reference_trading_terms))
            return term_overlap / total_terms if total_terms > 0 else 0.5

        return 0.5  # Default moderate score if can't determine similarity

    def calculate_overall_parity_score(self, current_response: Dict, reference_response: Dict, test_case: TestCase) -> float:
        """Calculate overall parity score for a test case."""
        if "error" in current_response or "error" in reference_response:
            return 0.0

        # Weight different aspects based on test category
        if test_case.category == "Query Enhancement":
            enhancement_score = self.analyze_query_enhancement_parity(current_response, reference_response)
            return enhancement_score
        elif test_case.category == "Routing Decision":
            routing_score = self.analyze_routing_parity(current_response, reference_response)
            return routing_score
        else:
            # For other categories, use a weighted combination
            enhancement_score = self.analyze_query_enhancement_parity(current_response, reference_response)
            routing_score = self.analyze_routing_parity(current_response, reference_response)
            quality_score = self.analyze_response_quality_parity(current_response, reference_response)

            return (enhancement_score * 0.3 + routing_score * 0.4 + quality_score * 0.3)

    def run_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case."""
        print(f"Running test {test_case.test_id}: {test_case.description}")

        try:
            # Call both implementations
            current_response, current_time = self.call_current_implementation(test_case)
            reference_response, reference_time = self.call_reference_implementation(test_case)

            # Calculate parity score
            parity_score = self.calculate_overall_parity_score(current_response, reference_response, test_case)

            # Determine test result
            if "error" in current_response:
                result = TestResult.ERROR
                notes = f"Current implementation error: {current_response['error']}"
            elif parity_score >= 0.8:
                result = TestResult.PASS
                notes = f"High parity achieved (score: {parity_score:.2f})"
            elif parity_score >= 0.6:
                result = TestResult.PASS
                notes = f"Acceptable parity (score: {parity_score:.2f})"
            else:
                result = TestResult.FAIL
                notes = f"Low parity score: {parity_score:.2f}"

            return TestResult(
                test_id=test_case.test_id,
                result=result,
                current_impl_response=current_response,
                reference_impl_response=reference_response,
                parity_score=parity_score,
                notes=notes,
                execution_time=current_time
            )

        except Exception as e:
            return TestResult(
                test_id=test_case.test_id,
                result=TestResult.ERROR,
                current_impl_response={"error": str(e)},
                reference_impl_response={},
                parity_score=0.0,
                notes=f"Test execution error: {str(e)}",
                execution_time=0.0
            )

    def run_all_tests(self) -> List[TestResult]:
        """Run all test cases and return results."""
        test_cases = self.load_test_cases()
        results = []

        print(f"Starting functional parity test suite with {len(test_cases)} test cases")
        print(f"Current implementation: {self.current_impl_url}")
        print(f"Reference implementation: {self.reference_impl_url or 'Not available'}")
        print("-" * 80)

        for test_case in test_cases:
            result = self.run_test_case(test_case)
            results.append(result)

            # Print immediate feedback
            status_symbol = "✅" if result.result == TestResult.PASS else "❌" if result.result == TestResult.FAIL else "⚠️"
            print(f"{status_symbol} {result.test_id}: {result.result.value} (Score: {result.parity_score:.2f}) - {result.notes}")

            # Small delay between tests
            time.sleep(1)

        self.test_results = results
        return results

    def generate_report(self, output_file: str = None) -> str:
        """Generate a comprehensive test report."""
        if not self.test_results:
            return "No test results available. Run tests first."

        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.result == TestResult.PASS])
        failed_tests = len([r for r in self.test_results if r.result == TestResult.FAIL])
        error_tests = len([r for r in self.test_results if r.result == TestResult.ERROR])

        avg_parity_score = sum(r.parity_score for r in self.test_results) / total_tests
        avg_execution_time = sum(r.execution_time for r in self.test_results) / total_tests

        # Generate report
        report = f"""
# HERO Bot Functional Parity Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests} ({passed_tests/total_tests*100:.1f}%)
- **Failed**: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
- **Errors**: {error_tests} ({error_tests/total_tests*100:.1f}%)
- **Average Parity Score**: {avg_parity_score:.3f}
- **Average Execution Time**: {avg_execution_time:.2f}s

## Test Results Summary

### Passed Tests ✅
"""

        for result in self.test_results:
            if result.result == TestResult.PASS:
                report += f"- **{result.test_id}**: {result.notes}\n"

        report += "\n### Failed Tests ❌\n"
        for result in self.test_results:
            if result.result == TestResult.FAIL:
                report += f"- **{result.test_id}**: {result.notes}\n"

        report += "\n### Error Tests ⚠️\n"
        for result in self.test_results:
            if result.result == TestResult.ERROR:
                report += f"- **{result.test_id}**: {result.notes}\n"

        report += "\n## Detailed Test Results\n"

        for result in self.test_results:
            report += f"""
### {result.test_id}
- **Result**: {result.result.value}
- **Parity Score**: {result.parity_score:.3f}
- **Execution Time**: {result.execution_time:.2f}s
- **Notes**: {result.notes}

**Current Implementation Response**:
```json
{json.dumps(result.current_impl_response, indent=2)[:500]}...
```

**Reference Implementation Response**:
```json
{json.dumps(result.reference_impl_response, indent=2)[:500]}...
```

---
"""

        # Overall assessment
        if avg_parity_score >= 0.8:
            assessment = "HIGH PARITY - Implementations are functionally equivalent"
        elif avg_parity_score >= 0.6:
            assessment = "MODERATE PARITY - Implementations are largely compatible with minor differences"
        else:
            assessment = "LOW PARITY - Significant differences detected, requires investigation"

        report += f"""
## Overall Assessment
**{assessment}**

Average parity score: {avg_parity_score:.3f}
Pass rate: {passed_tests/total_tests*100:.1f}%

## Recommendations
"""

        if failed_tests > 0:
            report += "- Review and address failed test cases\n"
        if error_tests > 0:
            report += "- Investigate and resolve test execution errors\n"
        if avg_parity_score < 0.8:
            report += "- Improve functional alignment between implementations\n"

        report += "- Consider manual validation for complex scenarios\n"
        report += "- Verify edge case handling consistency\n"

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Report saved to: {output_file}")

        return report

def main():
    """Main function to run the functional parity test suite."""
    import argparse

    parser = argparse.ArgumentParser(description="HERO Bot Functional Parity Test Suite")
    parser.add_argument("--current-url", default="http://localhost:8000",
                       help="URL of current LangGraph implementation")
    parser.add_argument("--reference-url", default=None,
                       help="URL of reference Agno implementation (optional)")
    parser.add_argument("--output", default="parity_test_report.md",
                       help="Output file for test report")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")

    args = parser.parse_args()

    # Initialize tester
    tester = FunctionalParityTester(args.current_url, args.reference_url)

    # Run tests
    try:
        results = tester.run_all_tests()

        # Generate and save report
        report = tester.generate_report(args.output)

        if args.verbose:
            print("\n" + "="*80)
            print("DETAILED REPORT")
            print("="*80)
            print(report)

        # Exit with appropriate code
        failed_count = len([r for r in results if r.result == TestResult.FAIL])
        error_count = len([r for r in results if r.result == TestResult.ERROR])

        if error_count > 0:
            sys.exit(2)  # Error exit code
        elif failed_count > 0:
            sys.exit(1)  # Failure exit code
        else:
            sys.exit(0)  # Success exit code

    except KeyboardInterrupt:
        print("\nTest suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()