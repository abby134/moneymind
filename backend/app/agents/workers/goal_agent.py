from anthropic import Anthropic
from app.agents.state import AgentState
from app.core.config import settings
import json

client = Anthropic(api_key=settings.anthropic_api_key)


async def goal_node(state: AgentState) -> dict:
    memory_context = state.get("memory_context", "")
    net_savings = sum(
        t["amount"] for t in state["transactions"] if not t.get("is_transfer")
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system="You are a financial goal tracker. Assess progress toward goals based on memory and current data. Respond in JSON.",
        messages=[{
            "role": "user",
            "content": f"""Month: {state['month']}
Net savings this month: ${net_savings:.2f}
Memory (contains goals and history): {memory_context}

Assess each goal mentioned in memory.
Respond as JSON: [{{"goal_name": "...", "on_track": bool, "assessment": "...", "recommendation": "..."}}]"""
        }]
    )

    text = response.content[0].text.strip()
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        goal_updates = json.loads(text[start:end])
    except Exception:
        goal_updates = []

    return {"goal_updates": goal_updates}
