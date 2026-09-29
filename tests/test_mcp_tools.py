from backend.mcp.registry import MCP_REGISTRY


def test_mcp_read_only_tool():
    res = MCP_REGISTRY.execute_tool(
        tool_id="search_public_information",
        event_id="evt_test",
        task_id="task_1",
        params={"query": "UK visa fees"}
    )
    assert res["status"] == "SUCCESS"


def test_mcp_action_tool_requires_approval():
    res = MCP_REGISTRY.execute_tool(
        tool_id="create_calendar_event",
        event_id="evt_test",
        task_id="task_2",
        params={"title": "GP Appointment", "date": "2026-10-15"}
    )
    assert res["status"] == "REQUIRES_APPROVAL"
    approval_id = res["approval_id"]

    # Test Approval
    appr_res = MCP_REGISTRY.approve_action(approval_id)
    assert appr_res["status"] == "SUCCESS"
