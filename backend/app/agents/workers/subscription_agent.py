from anthropic import Anthropic
from app.agents.state import AgentState
from app.core.config import settings
import json
from collections import defaultdict
from datetime import date, timedelta

client = Anthropic(api_key=settings.anthropic_api_key)


async def subscription_node(state: AgentState) -> dict:
    transactions = [t for t in state["transactions"] if t["amount"] < 0 and not t.get("is_transfer")]

    # Group by merchant to find recurring
    merchant_counts: dict[str, list] = defaultdict(list)
    for t in transactions:
        merchant = t.get("merchant") or t["description"]
        merchant_counts[merchant].append(abs(t["amount"]))

    # Flag merchants that appear consistently
    candidates = {
        merchant: amounts
        for merchant, amounts in merchant_counts.items()
        if len(amounts) >= 1 and max(amounts) < 500  # reasonable subscription amount
    }

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system="You are a subscription detector. Identify likely subscription charges and flag zombie ones. Respond in JSON.",
        messages=[{
            "role": "user",
            "content": f"""Potential subscription charges this month:
{json.dumps(candidates, indent=2)}

Historical memory: {state.get("memory_context", "")[:400]}

Identify subscriptions and flag any that seem unused (zombie subscriptions).
Respond as JSON: [{{"name": "...", "amount": 0, "is_zombie": bool, "reason": "..."}}]"""
        }]
    )

    text = response.content[0].text.strip()
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        subs = json.loads(text[start:end])
    except Exception:
        subs = []

    return {"subscription_updates": subs}
