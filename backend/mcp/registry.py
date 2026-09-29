from typing import Dict, Any, List, Optional
from backend.models.domain import MCPTool, ToolCategory, ApprovalRequest
from datetime import datetime


class MCPRegistry:
    """Model Context Protocol (MCP) Tool Registry with Human Approval Enforcement."""

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._pending_approvals: Dict[str, ApprovalRequest] = {}
        self._init_default_tools()

    def _init_default_tools(self):
        tools_def = [
            ("search_public_information", "Search public web index for general info", ToolCategory.READ_ONLY, False),
            ("search_official_source", "Search verified government and regulatory portals", ToolCategory.READ_ONLY, False),
            ("find_local_service", "Find nearby local public services and amenities", ToolCategory.READ_ONLY, False),
            ("geocode", "Convert addresses into geographic coordinates", ToolCategory.READ_ONLY, False),
            ("calculate_distance", "Calculate distance between two coordinates", ToolCategory.READ_ONLY, False),
            ("get_route", "Get driving or transit route directions", ToolCategory.READ_ONLY, False),
            ("get_weather", "Retrieve local current and forecasted weather", ToolCategory.READ_ONLY, False),
            ("get_local_time", "Get current time in specified timezone", ToolCategory.READ_ONLY, False),
            ("search_government_service", "Query government administrative service directories", ToolCategory.READ_ONLY, False),
            ("get_government_requirements", "Get official documentation and visa checklists", ToolCategory.READ_ONLY, False),
            ("search_school", "Discover elementary, primary, and secondary schools", ToolCategory.READ_ONLY, False),
            ("search_university", "Search higher education institutes and entry requirements", ToolCategory.READ_ONLY, False),
            ("search_hospital", "Find local healthcare providers and hospitals", ToolCategory.READ_ONLY, False),
            ("search_insurance", "Find local insurance providers and policies", ToolCategory.READ_ONLY, False),
            ("search_transportation", "Check local public transit and vehicle registration rules", ToolCategory.READ_ONLY, False),
            ("get_currency_rate", "Get real-time exchange rates between foreign currencies", ToolCategory.READ_ONLY, False),
            ("search_documents", "Search uploaded local document repository", ToolCategory.READ_ONLY, False),
            ("read_document", "Extract structured content from uploaded PDF/image documents", ToolCategory.READ_ONLY, False),
            
            # ACTION tools requiring human approval
            ("create_calendar_event", "Add deadline or appointment to user calendar", ToolCategory.ACTION, True),
            ("create_reminder", "Set persistent notification reminder", ToolCategory.ACTION, True),
            ("send_notification", "Send alert message via SMS/Email", ToolCategory.ACTION, True),
        ]

        for tool_id, desc, category, req_approval in tools_def:
            self._tools[tool_id] = MCPTool(
                tool_id=tool_id,
                name=tool_id.replace("_", " ").title(),
                description=desc,
                category=category,
                requires_approval=req_approval,
                parameters_schema={"type": "object", "properties": {}}
            )

    def list_tools(self) -> List[MCPTool]:
        return list(self._tools.values())

    def get_tool(self, tool_id: str) -> Optional[MCPTool]:
        return self._tools.get(tool_id)

    def execute_tool(self, tool_id: str, event_id: str, task_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        tool = self._tools.get(tool_id)
        if not tool:
            return {"status": "ERROR", "message": f"MCP Tool '{tool_id}' not found."}

        if tool.requires_approval:
            approval_id = f"appr_{len(self._pending_approvals) + 1}"
            appr = ApprovalRequest(
                approval_id=approval_id,
                event_id=event_id,
                task_id=task_id,
                tool_name=tool_id,
                parameters=params,
                reason=f"Execution of ACTION tool '{tool.name}' requires explicit human authorization.",
                status="PENDING"
            )
            self._pending_approvals[approval_id] = appr
            return {
                "status": "REQUIRES_APPROVAL",
                "approval_id": approval_id,
                "tool_id": tool_id,
                "message": f"Tool '{tool.name}' is an ACTION tool and requires explicit human approval."
            }

        # Mock tool execution return for READ_ONLY tools
        return {
            "status": "SUCCESS",
            "tool_id": tool_id,
            "result": {
                "params_received": params,
                "executed_at": datetime.utcnow().isoformat(),
                "data": f"Executed {tool.name} successfully."
            }
        }

    def list_pending_approvals(self) -> List[ApprovalRequest]:
        return [appr for appr in self._pending_approvals.values() if appr.status == "PENDING"]

    def approve_action(self, approval_id: str) -> Dict[str, Any]:
        appr = self._pending_approvals.get(approval_id)
        if not appr:
            return {"status": "ERROR", "message": "Approval request not found."}
        appr.status = "APPROVED"
        return {
            "status": "SUCCESS",
            "approval_id": approval_id,
            "tool_name": appr.tool_name,
            "message": f"Action tool '{appr.tool_name}' approved and executed."
        }

    def reject_action(self, approval_id: str) -> Dict[str, Any]:
        appr = self._pending_approvals.get(approval_id)
        if not appr:
            return {"status": "ERROR", "message": "Approval request not found."}
        appr.status = "REJECTED"
        return {
            "status": "SUCCESS",
            "approval_id": approval_id,
            "message": f"Action tool '{appr.tool_name}' rejected."
        }


# Global MCP Registry Singleton
MCP_REGISTRY = MCPRegistry()
