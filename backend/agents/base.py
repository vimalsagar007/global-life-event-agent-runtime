from typing import Dict, Any, List, Optional
from backend.models.domain import AgentCard, Task, TaskPriority, TaskStatus
from backend.a2a.bus import A2A_BUS
from backend.security.defense import SecurityGuard
from backend.observability.logger import get_or_create_trace
import time


class BaseAgent:
    """Base Specialist Agent class adhering to A2A standards."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        title: str,
        capabilities: List[str],
        skills: List[str],
        supported_input: List[str],
        supported_output: List[str]
    ):
        self.agent_id = agent_id
        self.name = name
        self.title = title
        self.capabilities = capabilities
        self.skills = skills
        self.supported_input = supported_input
        self.supported_output = supported_output

        # Register Agent Card in A2A Registry
        self.card = AgentCard(
            agent_id=self.agent_id,
            name=self.name,
            title=self.title,
            capabilities=self.capabilities,
            skills=self.skills,
            supported_input=self.supported_input,
            supported_output=self.supported_output,
            endpoint=f"/api/v1/a2a/{self.agent_id}",
            auth_required=True,
            status="ONLINE"
        )
        A2A_BUS.register_agent(self.card)

    def execute_task(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        start_time = time.time()
        trace = get_or_create_trace(event_id)

        # Screen input security
        raw_text = context.get("raw_input", "")
        passed, msg = SecurityGuard.inspect_prompt(raw_text)
        if not passed:
            trace.add_step(self.name, "SECURITY_BLOCKED", {"reason": msg}, (time.time() - start_time) * 1000)
            return []

        # Generate agent tasks
        tasks = self.generate_tasks(event_id, context)

        # Log trace step
        duration = (time.time() - start_time) * 1000
        trace.add_step(
            self.name,
            "TASK_GENERATION",
            {"tasks_count": len(tasks), "agent_title": self.title},
            duration
        )

        return tasks

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        """Subclasses override this to return specialized tasks."""
        return []
