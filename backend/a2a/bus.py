from typing import Dict, Any, List, Optional
from backend.models.domain import AgentCard


class AgentToAgentBus:
    """A2A (Agent-to-Agent) Messaging & Registry Bus."""

    def __init__(self):
        self._registry: Dict[str, AgentCard] = {}
        self._message_history: List[Dict[str, Any]] = []

    def register_agent(self, card: AgentCard):
        self._registry[card.agent_id] = card

    def get_agent_card(self, agent_id: str) -> Optional[AgentCard]:
        return self._registry.get(agent_id)

    def list_agent_cards(self) -> List[AgentCard]:
        return list(self._registry.values())

    def send_message(self, sender_id: str, recipient_id: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        sender = self._registry.get(sender_id)
        recipient = self._registry.get(recipient_id)

        if not recipient:
            return {
                "status": "ERROR",
                "message": f"Recipient agent '{recipient_id}' not found in A2A registry."
            }

        message_entry = {
            "message_id": f"msg_{len(self._message_history) + 1}",
            "sender": sender_id,
            "recipient": recipient_id,
            "action": action,
            "payload": payload,
            "status": "DELIVERED"
        }
        self._message_history.append(message_entry)

        # In-memory A2A protocol response simulation
        return {
            "status": "SUCCESS",
            "message_id": message_entry["message_id"],
            "recipient": recipient.name,
            "response": {
                "ack": True,
                "agent_status": recipient.status,
                "data": payload
            }
        }

    def get_message_history(self) -> List[Dict[str, Any]]:
        return self._message_history


# Global A2A Bus Singleton
A2A_BUS = AgentToAgentBus()
