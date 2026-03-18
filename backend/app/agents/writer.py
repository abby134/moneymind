from anthropic import Anthropic
from app.agents.state import AgentState
from app.core.config import settings
import json

client = Anthropic(api_key=settings.anthropic_api_key)


async def writer_node(state: AgentState) -> dict:
    """Generate the personalized monthly financial narrative."""
    transactions = [t for t in state["transactions"] if not t.get("is_transfer")]

    total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
    total_expenses = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    category_totals: dict[str, float] = {}
    for t in transactions:
        if t["amount"] < 0:
            cat = t.get("category", "other")
            category_totals[cat] = category_totals.get(cat, 0) + abs(t["amount"])

    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]

    verified_insights = state.get("verified_insights", [])
    anomalies = [a for a in state.get("anomalies", []) if a.get("is_truly_anomalous")]
    goal_updates = state.get("goal_updates", [])
    zombie_subs = [s for s in state.get("subscription_updates", []) if s.get("is_zombie")]

    # Prepare memory updates for save
    memory_updates = []
    for insight in verified_insights:
        memory_updates.append({
            "entity": "spending_pattern",
            "observation": insight["description"]
        })

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system="""You write warm, personal financial monthly letters.
Write like a trusted financial friend — honest but supportive.
Use markdown formatting. Keep it under 600 words.""",
        messages=[{
            "role": "user",
            "content": f"""Write the monthly financial letter for {state['month']}.

Financial summary:
- Income: ${total_income:.2f}
- Expenses: ${total_expenses:.2f}
- Net savings: ${net_savings:.2f}
- Savings rate: {savings_rate:.1f}%
- Top categories: {dict(top_categories)}

Verified behavioral patterns: {json.dumps(verified_insights, indent=2)}
Notable anomalies: {json.dumps(anomalies, indent=2)}
Goal updates: {json.dumps(goal_updates, indent=2)}
Zombie subscriptions found: {json.dumps(zombie_subs, indent=2)}

Write a personal letter starting with "## Your [Month] Financial Letter" """
        }]
    )

    report_md = response.content[0].text

    return {
        "report_md": report_md,
        "memory_updates": memory_updates,
    }
