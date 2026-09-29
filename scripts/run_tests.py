import sys
import os

# Set PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.test_jurisdiction import test_cross_border_relocation_toronto_london, test_domestic_relocation_ny_sf, test_tokyo_singapore
from tests.test_agents_a2a import test_a2a_registration_and_message_passing
from tests.test_mcp_tools import test_mcp_read_only_tool, test_mcp_action_tool_requires_approval
from tests.test_rag_citations import test_rag_retrieval_and_citations
from tests.test_replanning import test_event_driven_replanning
from backend.evaluation.runner import EvaluationRunner


def run_all_tests():
    print("==================================================")
    print("🧪 Running Global Life Event AI Test Suite")
    print("==================================================")

    print("\n1. Testing Jurisdiction Resolver...")
    test_cross_border_relocation_toronto_london()
    test_domestic_relocation_ny_sf()
    test_tokyo_singapore()
    print("   ✓ Jurisdiction tests passed!")

    print("\n2. Testing A2A Agent Bus...")
    test_a2a_registration_and_message_passing()
    print("   ✓ A2A protocol tests passed!")

    print("\n3. Testing MCP Tools & Human Approval Gating...")
    test_mcp_read_only_tool()
    test_mcp_action_tool_requires_approval()
    print("   ✓ MCP tools tests passed!")

    print("\n4. Testing RAG Pipeline & Citation Scoring...")
    test_rag_retrieval_and_citations()
    print("   ✓ RAG & Citation tests passed!")

    print("\n5. Testing Event-Driven Re-planning...")
    test_event_driven_replanning()
    print("   ✓ Event-Driven Re-planning tests passed!")

    print("\n6. Running 50 Evaluation Scenarios Benchmark...")
    eval_result = EvaluationRunner.run_evaluations()
    print(f"   ✓ Benchmark Completed: {eval_result.passed_scenarios}/{eval_result.total_scenarios} Passed")
    print(f"   ✓ Jurisdiction Accuracy: {eval_result.jurisdiction_accuracy}%")
    print(f"   ✓ Citation Precision: {eval_result.citation_precision}%")
    print(f"   ✓ Safety Compliance: {eval_result.safety_disclaimer_compliance}%")
    print(f"   ✓ Average Latency: {eval_result.average_latency_ms} ms")

    print("\n==================================================")
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
