from anthropic import Anthropic
from app.agents.state import AgentState, PatternInsight
from app.core.config import settings
import json

client = Anthropic(api_key=settings.anthropic_api_key)


async def pattern_node(state: AgentState) -> dict:
    transactions = [t for t in state["transactions"] if not t.get("is_transfer")]
    memory_context = state.get("memory_context", "")

    category_totals: dict[str, float] = {}
    for t in transactions:
        if t["amount"] < 0:
            cat = t.get("category", "other")
            category_totals[cat] = category_totals.get(cat, 0) + abs(t["amount"])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system="""You are a financial pattern analyst. Identify behavioral patterns by comparing
current spending to historical memory. Only report patterns supported by the memory context.
Respond in JSON array format.""",
        messages=[{
            "role": "user",
            "content": f"""Current month spending by category:
{json.dumps(category_totals, indent=2)}

Historical memory:
{memory_context}

Identify patterns. For each pattern include:
- type: "recurring_overspend" | "improvement" | "seasonal" | "new_behavior"
- description: human readable explanation
- supporting_months: list of months that support this pattern
- confidence: 0.0-1.0

Respond as JSON array only."""
        }]
    )

    text = response.content[0].text.strip()
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        insights = json.loads(text[start:end])
        for insight in insights:
            insight["source_verified"] = False
    except Exception:
        insights = []

    return {"pattern_insights": insights}
