from typing import Dict, Any, List, Optional
from backend.models.domain import LifeEvent


class MemoryStore:
    """In-Memory and Persistent State Store for Events, Conversations, and User Preferences."""

    def __init__(self):
        self._events: Dict[str, LifeEvent] = {}
        self._user_preferences: Dict[str, Any] = {
            "preferred_language": "en",
            "preferred_currency": "USD",
            "notification_preference": "EMAIL",
            "privacy_mode": "STANDARD"
        }
        self._conversations: List[Dict[str, Any]] = []

    def save_event(self, event: LifeEvent):
        self._events[event.event_id] = event

    def get_event(self, event_id: str) -> Optional[LifeEvent]:
        return self._events.get(event_id)

    def list_events(self) -> List[LifeEvent]:
        return list(self._events.values())

    def update_user_preferences(self, prefs: Dict[str, Any]):
        self._user_preferences.update(prefs)

    def get_user_preferences(self) -> Dict[str, Any]:
        return self._user_preferences

    def add_conversation_turn(self, role: str, content: str):
        self._conversations.append({"role": role, "content": content})

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        return self._conversations

    def delete_event(self, event_id: str) -> bool:
        if event_id in self._events:
            del self._events[event_id]
            return True
        return False

    def clear_all_memory(self):
        self._events.clear()
        self._conversations.clear()


# Global Memory Store Singleton
MEMORY_STORE = MemoryStore()
