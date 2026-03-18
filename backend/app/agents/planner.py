from anthropic import Anthropic
from app.agents.state import AgentState
from app.core.config import settings
import json

client = Anthropic(api_key=settings.anthropic_api_key)


async def planner_node(state: AgentState) -> AgentState:
    transactions = state["transactions"]
    memory_context = state.get("memory_context", "No previous history.")

    total_income = sum(t["amount"] for t in transactions if t["amount"] > 0 and not t.get("is_transfer"))
    total_expenses = sum(t["amount"] for t in transactions if t["amount"] < 0 and not t.get("is_transfer"))
    num_transactions = len(transactions)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system="You are a financial analysis planner. Summarize what analysis is needed based on the data.",
        messages=[{
            "role": "user",
            "content": f"""Month: {state['month']}
Transactions: {num_transactions} total
Income: ${total_income:.2f}
Expenses: ${total_expenses:.2f}
Memory context: {memory_context[:500]}

List the top 3 most important things to analyze this month."""
        }]
    )

    return {"errors": []}
