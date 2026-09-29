from typing import List, Dict, Any, Callable
from backend.models.domain import EventNotification


class EventBus:
    """Simulated Pub/Sub Event Bus for Event-Driven Re-planning."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[EventNotification], None]]] = {}
        self._event_history: List[EventNotification] = []

    def subscribe(self, event_type: str, callback: Callable[[EventNotification], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, notification: EventNotification):
        self._event_history.append(notification)
        callbacks = self._subscribers.get(notification.event_type, [])
        for cb in callbacks:
            try:
                cb(notification)
            except Exception as e:
                print(f"Error executing Pub/Sub callback for {notification.event_type}: {e}")

    def get_event_history(self) -> List[EventNotification]:
        return self._event_history


# Global Event Bus Singleton
EVENT_BUS = EventBus()
