from backend.a2a.bus import A2A_BUS
from backend.agents.specialists import GovernmentAgent, ImmigrationAgent


def test_a2a_registration_and_message_passing():
    gov = GovernmentAgent()
    imm = ImmigrationAgent()

    cards = A2A_BUS.list_agent_cards()
    assert len(cards) >= 2

    gov_card = A2A_BUS.get_agent_card("gov_agent")
    assert gov_card is not None
    assert gov_card.name == "GovernmentAgent"

    # Send A2A message
    res = A2A_BUS.send_message(
        sender_id="gov_agent",
        recipient_id="imm_agent",
        action="REQUEST_VISA_REQUIREMENTS",
        payload={"country": "United Kingdom"}
    )

    assert res["status"] == "SUCCESS"
    assert res["recipient"] == "ImmigrationAgent"
