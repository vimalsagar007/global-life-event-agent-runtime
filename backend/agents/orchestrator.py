import uuid
from typing import Dict, Any, List, Optional
from backend.models.domain import LifeEvent, Task, TaskStatus, TaskPriority, Jurisdiction
from backend.jurisdiction.resolver import JurisdictionResolver
from backend.agents.specialists import (
    GovernmentAgent, EducationAgent, ImmigrationAgent, HousingAgent,
    HealthcareAgent, FinanceAgent, TransportationAgent, PetRelocationAgent, CrossBorderAgent
)
from backend.a2a.bus import A2A_BUS
from backend.memory.store import MEMORY_STORE
from backend.events.pubsub import EVENT_BUS, EventNotification


class LifeEventOrchestrator:
    """Central Life Event AI Orchestrator & Dependency Graph Engine."""

    def __init__(self):
        # Register specialist agents
        self.specialists = [
            GovernmentAgent(),
            ImmigrationAgent(),
            HousingAgent(),
            EducationAgent(),
            FinanceAgent(),
            HealthcareAgent(),
            TransportationAgent(),
            PetRelocationAgent(),
            CrossBorderAgent()
        ]

        # Subscribe to source change notifications for automatic re-planning
        EVENT_BUS.subscribe("SOURCE_CHANGED", self._handle_source_change_event)

    def orchestrate_event(self, raw_input: str, user_override: Optional[Dict[str, Any]] = None) -> LifeEvent:
        event_id = f"evt_{uuid.uuid4().hex[:8]}"

        # 1. Resolve Jurisdiction
        orig_juris, dest_juris, is_cross_border = JurisdictionResolver.resolve_from_text(raw_input)

        if user_override and "origin_country" in user_override:
            orig_juris.country = user_override["origin_country"]
        if user_override and "destination_country" in user_override:
            if not dest_juris:
                dest_juris = Jurisdiction(country=user_override["destination_country"])
            else:
                dest_juris.country = user_override["destination_country"]

        # 2. Extract affected entities & assets
        text_lower = raw_input.lower()
        affected_people = {}
        if "children" in text_lower or "child" in text_lower or "school" in text_lower:
            affected_people["children"] = 2 if "two" in text_lower else 1
        if "spouse" in text_lower or "partner" in text_lower or "married" in text_lower:
            affected_people["spouse"] = 1

        assets = []
        if "car" in text_lower or "vehicle" in text_lower:
            assets.append("vehicle")
        if "dog" in text_lower or "pet" in text_lower or "cat" in text_lower:
            assets.append("pet")
        if "company" in text_lower or "business" in text_lower:
            assets.append("business")

        # Context payload for agents
        context = {
            "raw_input": raw_input,
            "origin_jurisdiction": orig_juris,
            "destination_jurisdiction": dest_juris,
            "is_cross_border": is_cross_border,
            "affected_people": affected_people,
            "assets": assets
        }

        # 3. Delegate to Specialist Agents via A2A
        all_tasks: List[Task] = []
        domains: List[str] = []

        for agent in self.specialists:
            agent_tasks = agent.execute_task(event_id, context)
            if agent_tasks:
                all_tasks.extend(agent_tasks)
                domains.append(agent.name.replace("Agent", ""))

        # 4. Build Dependency Graph
        self._build_dependency_graph(all_tasks)

        life_event = LifeEvent(
            event_id=event_id,
            title=f"Execution Plan: {raw_input[:60]}...",
            raw_input=raw_input,
            event_type="CROSS_BORDER_RELOCATION" if is_cross_border else "DOMESTIC_RELOCATION",
            origin_jurisdiction=orig_juris,
            destination_jurisdiction=dest_juris,
            is_cross_border=is_cross_border,
            affected_people=affected_people,
            assets=assets,
            domains=domains,
            tasks=all_tasks,
            status="ACTIVE"
        )

        # 5. Store Event in Memory
        MEMORY_STORE.save_event(life_event)

        return life_event

    def _build_dependency_graph(self, tasks: List[Task]):
        """Sets topological execution order dependencies between tasks."""
        imm_tasks = [t for t in tasks if t.category == "Immigration"]
        gov_tasks = [t for t in tasks if t.category == "Government"]
        house_tasks = [t for t in tasks if t.category == "Housing"]
        edu_tasks = [t for t in tasks if t.category == "Education"]
        trans_tasks = [t for t in tasks if t.category == "Transportation"]
        fin_tasks = [t for t in tasks if t.category == "Finance"]

        # Housing & Banking depend on Immigration clearance if cross-border
        if imm_tasks:
            imm_id = imm_tasks[0].task_id
            for t in house_tasks + fin_tasks:
                t.dependencies.append(imm_id)

        # Schooling & License transfer depend on securing Housing/Address
        if house_tasks:
            house_id = house_tasks[0].task_id
            for t in edu_tasks + trans_tasks + gov_tasks:
                t.dependencies.append(house_id)

    def _handle_source_change_event(self, notification: EventNotification):
        """Dynamic Re-planning handler triggered when a regulatory source changes."""
        event_id = notification.event_id
        life_event = MEMORY_STORE.get_event(event_id)
        if not life_event:
            return

        print(f"[RE-PLANNER] Re-planning triggered for Event {event_id} due to source update.")
        
        # Add updated task to plan
        new_task = Task(
            task_id=f"replan_{event_id}_{len(life_event.tasks) + 1}",
            title="UPDATED REQUIREMENT: Re-verify NHS/Government Registration Rules",
            description="Compliance alert: Updated regulatory policy detected in official portal. Immediate action required.",
            category="Compliance Update",
            jurisdiction=life_event.destination_jurisdiction.country if life_event.destination_jurisdiction else "Global",
            priority=TaskPriority.CRITICAL,
            status=TaskStatus.REQUIRES_APPROVAL,
            deadline="Immediate",
            sources=[],
            agent="ComplianceAgent",
            requires_approval=True
        )
        life_event.tasks.append(new_task)
        life_event.updated_at = notification.timestamp
        MEMORY_STORE.save_event(life_event)


# Global Orchestrator Singleton
ORCHESTRATOR = LifeEventOrchestrator()
