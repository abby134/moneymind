from anthropic import Anthropic
from app.agents.state import AgentState
from app.core.config import settings
import json
import statistics

client = Anthropic(api_key=settings.anthropic_api_key)


async def anomaly_node(state: AgentState) -> dict:
    transactions = [t for t in state["transactions"] if not t.get("is_transfer") and t["amount"] < 0]

    if not transactions:
        return {"anomalies": []}

    amounts = [abs(t["amount"]) for t in transactions]
    mean = statistics.mean(amounts)
    stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0
    threshold = mean + (2.5 * stdev)

    large_transactions = [
        t for t in transactions if abs(t["amount"]) > threshold
    ]

    if not large_transactions:
        return {"anomalies": []}

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system="You are a financial anomaly analyst. Explain unusual transactions clearly. Respond in JSON array.",
        messages=[{
            "role": "user",
            "content": f"""These transactions are statistically unusual (>{threshold:.0f} vs avg ${mean:.0f}):
{json.dumps([{"desc": t["description"], "amount": t["amount"], "merchant": t.get("merchant")} for t in large_transactions], indent=2)}

Memory context: {state.get("memory_context", "")[:300]}

For each, explain if it's truly anomalous or explainable.
Respond as JSON: [{{"description": "...", "amount": 0, "is_truly_anomalous": bool, "explanation": "..."}}]"""
        }]
    )

    text = response.content[0].text.strip()
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        anomalies = json.loads(text[start:end])
    except Exception:
        anomalies = []

    return {"anomalies": anomalies}
