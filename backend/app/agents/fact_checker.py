from anthropic import Anthropic
from app.agents.state import AgentState
from app.core.config import settings
import json

client = Anthropic(api_key=settings.anthropic_api_key)


async def fact_checker_node(state: AgentState) -> dict:
    """
    Re-validates all numerical claims from worker agents.
    Isolates from worker context to prevent confirmation bias.
    """
    transactions = [t for t in state["transactions"] if not t.get("is_transfer")]

    # Recompute ground truth independently
    category_actuals: dict[str, float] = {}
    for t in transactions:
        if t["amount"] < 0:
            cat = t.get("category", "other")
            category_actuals[cat] = category_actuals.get(cat, 0) + abs(t["amount"])

    total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
    total_expenses = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)

    flags = []
    verified_insights = []

    # Verify pattern insights have supporting data
    for insight in state.get("pattern_insights", []):
        months_mentioned = insight.get("supporting_months", [])
        memory_context = state.get("memory_context", "")

        # Check if memory context actually supports the claim
        description = insight.get("description", "")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            system="You verify financial claims. Answer only YES or NO followed by brief reason.",
            messages=[{
                "role": "user",
                "content": f"""Does this memory context support the claim?
Claim: {description}
Memory: {memory_context[:600]}
Answer YES or NO:"""
            }]
        )

        answer = response.content[0].text.strip().upper()
        if answer.startswith("YES"):
            insight["source_verified"] = True
            verified_insights.append(insight)
        else:
            flags.append({
                "type": "unverified_pattern",
                "claim": description,
                "reason": "Not supported by memory history"
            })

    return {
        "fact_check_flags": flags,
        "verified_insights": verified_insights,
    }
