from backend.agents.orchestrator import ORCHESTRATOR
from backend.events.pubsub import EVENT_BUS, EventNotification
from backend.memory.store import MEMORY_STORE


def test_event_driven_replanning():
    event = ORCHESTRATOR.orchestrate_event("I am moving from Toronto to London")
    initial_tasks_count = len(event.tasks)

    notification = EventNotification(
        event_type="SOURCE_CHANGED",
        event_id=event.event_id,
        message="SIMULATED SOURCE CHANGE",
        details={"source": "src_uk_nhs_2026"}
    )
    EVENT_BUS.publish(notification)

    updated_event = MEMORY_STORE.get_event(event.event_id)
    assert len(updated_event.tasks) == initial_tasks_count + 1
    assert updated_event.tasks[-1].category == "Compliance Update"
