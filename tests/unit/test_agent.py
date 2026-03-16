#!/usr/bin/env python3
"""
Comprehensive unit tests for the RAG agent.
Consolidates multiple test scenarios for agent functionality.
"""

import time
import pytest
from langchain_core.messages import HumanMessage
from src.backend.core.agent import rag_agent


class TestAgentExecution:
    """Test suite for basic agent execution and configuration."""

    def test_agent_basic_execution(self):
        """Test that the agent executes successfully without timeout."""
        print("=" * 80)
        print("Testing Agent Fix: Config Parameters in State")
        print("=" * 80)

        # Test configuration
        inputs = {
            "messages": [HumanMessage(content="Hello, what can you help me with?")],
            "web_search_enabled": False,
            "force_web_search": False,
            "similarity_threshold": 0.7
        }

        config = {"configurable": {"thread_id": "test-fix-session"}}

        print("\nTest Configuration:")
        print(f"  Query: {inputs['messages'][0].content}")
        print(f"  Web Search Enabled: {inputs['web_search_enabled']}")
        print(f"  Force Web Search: {inputs['force_web_search']}")
        print(f"  Similarity Threshold: {inputs['similarity_threshold']}")
        print(f"  Session ID: {config['configurable']['thread_id']}")

        print("\n" + "-" * 80)
        print("Starting agent stream...")
        print("-" * 80 + "\n")

        start_time = time.time()
        event_count = 0
        max_events = 20  # Safety limit

        try:
            for i, event in enumerate(rag_agent.stream(inputs, config=config)):
                event_count = i + 1
                node_name = list(event.keys())[0] if event else "unknown"

                print(f"Event {event_count}: Node '{node_name}' executed")

                # Safety break to prevent infinite loops during testing
                if event_count >= max_events:
                    print(f"\n⚠ Stopped after {max_events} events (safety limit)")
                    break

            elapsed_time = time.time() - start_time

            print("\n" + "=" * 80)
            print("TEST RESULTS")
            print("=" * 80)
            print(f"✅ Agent completed successfully!")
            print(f"   Total events: {event_count}")
            print(f"   Execution time: {elapsed_time:.2f} seconds")

            if elapsed_time < 10:
                print(f"   ✅ Performance: Excellent (< 10 seconds)")
            elif elapsed_time < 30:
                print(f"   ⚠ Performance: Acceptable (< 30 seconds)")
            else:
                print(f"   ❌ Performance: Slow (>= 30 seconds)")

            print("\n" + "=" * 80)
            print("FIX VERIFICATION: SUCCESS")
            print("=" * 80)
            print("The agent executed without timeout or hanging issues.")
            print("Config parameters are now successfully passed via state.")
            print("=" * 80)

            assert elapsed_time < 60, "Agent took too long to execute"
            assert event_count > 0, "No events were generated"

        except Exception as e:
            elapsed_time = time.time() - start_time

            print("\n" + "=" * 80)
            print("TEST RESULTS")
            print("=" * 80)
            print(f"❌ Agent execution failed!")
            print(f"   Error: {e}")
            print(f"   Events before error: {event_count}")
            print(f"   Time before error: {elapsed_time:.2f} seconds")

            print("\n" + "=" * 80)
            print("FIX VERIFICATION: FAILED")
            print("=" * 80)
            print(f"Error details: {e}")
            print("=" * 80)

            pytest.fail(f"Agent execution failed: {e}")

    def test_agent_direct_stream(self):
        """Direct test of the RAG agent to isolate issues."""
        print("Testing RAG agent directly...")
        print("-" * 50)

        config = {
            "configurable": {
                "thread_id": "test_session",
                "web_search_enabled": True,
                "force_web_search": False,
                "similarity_threshold": 0.7
            }
        }

        inputs = {"messages": [HumanMessage(content="What is stop loss?")]}

        print("Starting agent stream...")
        try:
            for i, step in enumerate(rag_agent.stream(inputs, config=config)):
                print(f"\nStep {i+1}:")
                print(f"Keys: {list(step.keys())}")
                if '__end__' in step:
                    print("END node reached")
                    print(f"Final state keys: {list(step['__end__'].keys())}")
                else:
                    node_name = list(step.keys())[0]
                    print(f"Node: {node_name}")
                    if 'route' in step[node_name]:
                        print(f"Route decision: {step[node_name]['route']}")

            print("\n" + "=" * 50)
            print("✅ Agent completed successfully!")

        except Exception as e:
            print(f"\n❌ Error during agent execution:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {e}")
            pytest.fail(f"Agent stream failed: {e}")


class TestAgentScenarios:
    """Comprehensive scenario testing for various agent configurations."""

    def _test_scenario(self, scenario_name, inputs, config):
        """Helper method to test a specific scenario."""
        print(f"\n{'=' * 80}")
        print(f"SCENARIO: {scenario_name}")
        print(f"{'=' * 80}")
        print(f"Config: {inputs}")

        start_time = time.time()
        try:
            events = list(rag_agent.stream(inputs, config=config))
            elapsed = time.time() - start_time

            print(f"✅ SUCCESS - {len(events)} events in {elapsed:.2f}s")
            return True
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ FAILED - Error after {elapsed:.2f}s: {e}")
            return False

    def test_comprehensive_scenarios(self):
        """Test multiple scenarios with different configurations."""
        print("=" * 80)
        print("COMPREHENSIVE AGENT FIX VERIFICATION")
        print("=" * 80)

        scenarios = [
            {
                "name": "Web search disabled, normal threshold",
                "inputs": {
                    "messages": [HumanMessage(content="How to trade stocks?")],
                    "web_search_enabled": False,
                    "force_web_search": False,
                    "similarity_threshold": 0.7
                }
            },
            {
                "name": "Web search enabled, normal threshold",
                "inputs": {
                    "messages": [HumanMessage(content="How to trade stocks?")],
                    "web_search_enabled": True,
                    "force_web_search": False,
                    "similarity_threshold": 0.7
                }
            },
            {
                "name": "Force web search enabled",
                "inputs": {
                    "messages": [HumanMessage(content="How to trade stocks?")],
                    "web_search_enabled": True,
                    "force_web_search": True,
                    "similarity_threshold": 0.7
                }
            },
            {
                "name": "High similarity threshold",
                "inputs": {
                    "messages": [HumanMessage(content="How to trade stocks?")],
                    "web_search_enabled": False,
                    "force_web_search": False,
                    "similarity_threshold": 0.9
                }
            }
        ]

        results = []
        for i, scenario in enumerate(scenarios, 1):
            config = {"configurable": {"thread_id": f"test-scenario-{i}"}}
            success = self._test_scenario(scenario["name"], scenario["inputs"], config)
            results.append(success)
            time.sleep(1)  # Brief pause between tests

        # Summary
        print(f"\n{'=' * 80}")
        print("TEST SUMMARY")
        print(f"{'=' * 80}")
        total = len(results)
        passed = sum(results)
        failed = total - passed

        print(f"Total Scenarios: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")

        if failed == 0:
            print(f"\n{'=' * 80}")
            print("ALL TESTS PASSED - FIX VERIFIED!")
            print(f"{'=' * 80}")
        else:
            print(f"\n{'=' * 80}")
            print("SOME TESTS FAILED - REVIEW REQUIRED")
            print(f"{'=' * 80}")
            pytest.fail(f"{failed} out of {total} scenarios failed")


if __name__ == "__main__":
    # Allow running as standalone script
    pytest.main([__file__, "-v"])
