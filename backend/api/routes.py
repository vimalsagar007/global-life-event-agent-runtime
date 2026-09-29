import json
import os
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from backend.models.domain import LifeEvent, Task, ApprovalRequest
from backend.agents.orchestrator import ORCHESTRATOR
from backend.a2a.bus import A2A_BUS
from backend.mcp.registry import MCP_REGISTRY
from backend.memory.store import MEMORY_STORE
from backend.observability.logger import TRACE_STORE
from backend.rag.pipeline import RAG_PIPELINE
from backend.events.pubsub import EVENT_BUS, EventNotification
from backend.evaluation.runner import EvaluationRunner

router = APIRouter()

DEMO_SCENARIOS_PATH = os.path.join(os.path.dirname(__file__), "../../demo-data/scenarios.json")


@router.post("/events", response_model=LifeEvent)
def create_life_event(payload: Dict[str, Any] = Body(...)):
    raw_input = payload.get("raw_input")
    if not raw_input:
        raise HTTPException(status_code=400, detail="Field 'raw_input' is required.")
    
    user_override = payload.get("user_override")
    event = ORCHESTRATOR.orchestrate_event(raw_input, user_override)
    return event


@router.get("/events/{event_id}", response_model=LifeEvent)
def get_life_event(event_id: str):
    event = MEMORY_STORE.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Life Event not found.")
    return event


@router.get("/events/{event_id}/tasks", response_model=List[Task])
def get_event_tasks(event_id: str):
    event = MEMORY_STORE.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Life Event not found.")
    return event.tasks


@router.post("/events/{event_id}/replan")
def replan_event(event_id: str):
    event = MEMORY_STORE.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Life Event not found.")
    
    notification = EventNotification(
        event_type="SOURCE_CHANGED",
        event_id=event_id,
        message="Manual re-plan requested due to regulatory update.",
        details={"reason": "User requested manual re-plan"}
    )
    EVENT_BUS.publish(notification)
    
    updated_event = MEMORY_STORE.get_event(event_id)
    return {"status": "SUCCESS", "event": updated_event}


@router.post("/tasks/{task_id}/approve")
def approve_task(task_id: str):
    result = MCP_REGISTRY.approve_action(task_id)
    return result


@router.post("/tasks/{task_id}/reject")
def reject_task(task_id: str):
    result = MCP_REGISTRY.reject_action(task_id)
    return result


@router.get("/events/{event_id}/activity")
def get_event_activity(event_id: str):
    trace = TRACE_STORE.get(event_id)
    if not trace:
        return {"trace_id": f"trace_{event_id}", "event_id": event_id, "steps": [], "total_duration_ms": 0}
    return trace


@router.get("/events/{event_id}/sources")
def get_event_sources(event_id: str):
    event = MEMORY_STORE.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Life Event not found.")
    
    sources = []
    for t in event.tasks:
        sources.extend([s.model_dump() for s in t.sources])
    return sources


@router.get("/agents")
def list_agents():
    return [a.model_dump() for a in A2A_BUS.list_agent_cards()]


@router.get("/a2a/agents")
def list_a2a_cards():
    return [a.model_dump() for a in A2A_BUS.list_agent_cards()]


@router.get("/mcp/tools")
def list_mcp_tools():
    return [t.model_dump() for t in MCP_REGISTRY.list_tools()]


@router.get("/mcp/pending-approvals", response_model=List[ApprovalRequest])
def list_pending_approvals():
    return MCP_REGISTRY.list_pending_approvals()


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()
    
    # Simulate Gemini Multimodal extraction
    extracted = {
        "filename": filename,
        "size_bytes": len(content),
        "document_type": "PDF / Image Document",
        "extracted_summary": f"Extracted text and metadata from uploaded document '{filename}'. Verified dates, names, and address elements.",
        "notice": "Extracted from uploaded document — please verify."
    }
    return extracted


@router.post("/search")
def search_knowledge_base(payload: Dict[str, Any] = Body(...)):
    query = payload.get("query", "")
    country = payload.get("country")
    results = RAG_PIPELINE.retrieve(query, country=country)
    return [r.model_dump() for r in results]


@router.get("/demo/scenarios")
def get_demo_scenarios():
    if os.path.exists(DEMO_SCENARIOS_PATH):
        with open(DEMO_SCENARIOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@router.post("/demo/simulate-source-change")
def simulate_source_change(payload: Dict[str, Any] = Body(...)):
    event_id = payload.get("event_id")
    if not event_id:
        # Create a new demo event first if not provided
        demo_event = ORCHESTRATOR.orchestrate_event("I am moving from Toronto to London")
        event_id = demo_event.event_id

    notification = EventNotification(
        event_type="SOURCE_CHANGED",
        source_id="src_uk_nhs_2026",
        event_id=event_id,
        message="SIMULATED SOURCE CHANGE: UK Healthcare Surcharge Policy updated on official portal.",
        details={"updated_field": "Healthcare Surcharge Fee", "old_val": "£1035/yr", "new_val": "£1150/yr"}
    )
    EVENT_BUS.publish(notification)

    updated_event = MEMORY_STORE.get_event(event_id)
    return {
        "status": "SOURCE_CHANGED_SIMULATED",
        "event_id": event_id,
        "notification": notification.model_dump(),
        "updated_event": updated_event
    }


@router.post("/evaluation/run")
def run_evaluation_benchmark():
    results = EvaluationRunner.run_evaluations()
    return results


@router.get("/memory/preferences")
def get_memory_preferences():
    return MEMORY_STORE.get_user_preferences()


@router.delete("/memory")
def clear_memory():
    MEMORY_STORE.clear_all_memory()
    return {"status": "SUCCESS", "message": "All event memory and conversation history cleared."}
