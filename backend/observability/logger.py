import time
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GlobalLifeEventAI")


class TraceStep(BaseModel):
    step_id: str
    agent_name: str
    action_type: str  # PLAN, DELEGATE, MCP_TOOL, RAG_SEARCH, COMPLIANCE
    details: Dict[str, Any]
    duration_ms: float
    timestamp: float = Field(default_factory=time.time)


class ExecutionTrace(BaseModel):
    trace_id: str
    event_id: str
    steps: List[TraceStep] = Field(default_factory=list)
    total_duration_ms: float = 0.0

    def add_step(self, agent_name: str, action_type: str, details: Dict[str, Any], duration_ms: float):
        step = TraceStep(
            step_id=f"step_{len(self.steps) + 1}",
            agent_name=agent_name,
            action_type=action_type,
            details=details,
            duration_ms=duration_ms
        )
        self.steps.append(step)
        self.total_duration_ms += duration_ms
        logger.info(f"[{self.trace_id}] {agent_name} -> {action_type} ({duration_ms:.1f}ms)")


# Global trace store in memory
TRACE_STORE: Dict[str, ExecutionTrace] = {}


def get_or_create_trace(event_id: str) -> ExecutionTrace:
    if event_id not in TRACE_STORE:
        TRACE_STORE[event_id] = ExecutionTrace(trace_id=f"trace_{event_id}", event_id=event_id)
    return TRACE_STORE[event_id]
