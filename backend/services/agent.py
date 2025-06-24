from typing import List, Dict, Any
from main import (
    triage_agent,
    faq_agent,
    order_placement_agent,
    order_status_agent,
    reservation_agent,
    offers_agent,
)
from services.guardrail import get_guardrail_name

def get_agent_by_name(name: str):
    """Return the agent object by name."""
    agents = {
        triage_agent.name: triage_agent,
        faq_agent.name: faq_agent,
        order_placement_agent.name: order_placement_agent,
        order_status_agent.name: order_status_agent,
        reservation_agent.name: reservation_agent,
        offers_agent.name: offers_agent,
    }
    return agents.get(name, triage_agent)

def build_agents_list() -> List[Dict[str, Any]]:
    """Build a list of all available agents and their metadata."""
    def make_agent_dict(agent):
        return {
            "name": agent.name,
            "description": getattr(agent, "handoff_description", ""),
            "handoffs": [getattr(h, "agent_name", getattr(h, "name", "")) for h in getattr(agent, "handoffs", [])],
            "tools": [getattr(t, "name", getattr(t, "__name__", "")) for t in getattr(agent, "tools", [])],
            "input_guardrails": [get_guardrail_name(g) for g in getattr(agent, "input_guardrails", [])],
        }
    return [
        make_agent_dict(triage_agent),
        make_agent_dict(faq_agent),
        make_agent_dict(order_placement_agent),
        make_agent_dict(order_status_agent),
        make_agent_dict(reservation_agent),
        make_agent_dict(offers_agent),
    ]