from app.agents.state import AgentState
from datetime import date, timedelta
import uuid


async def transfer_node(state: AgentState) -> dict:
    """Detect inter-account transfers by matching amount + date proximity."""
    transactions = state["transactions"]

    positives = [t for t in transactions if t["amount"] > 0]
    negatives = [t for t in transactions if t["amount"] < 0]

    transfer_pairs = []
    matched_ids = set()

    for neg in negatives:
        if neg["id"] in matched_ids:
            continue
        for pos in positives:
            if pos["id"] in matched_ids:
                continue

            # Match: same amount, within 2 days
            amount_match = abs(abs(neg["amount"]) - pos["amount"]) < 0.01

            neg_date = date.fromisoformat(str(neg["date"]))
            pos_date = date.fromisoformat(str(pos["date"]))
            date_close = abs((neg_date - pos_date).days) <= 2

            # Check if description suggests transfer
            transfer_keywords = ["transfer", "xfer", "zelle", "ach", "wire", "from ", "to "]
            desc_suggests = any(
                kw in neg["description"].lower() or kw in pos["description"].lower()
                for kw in transfer_keywords
            )

            if amount_match and date_close and desc_suggests:
                pair_id = str(uuid.uuid4())
                transfer_pairs.append({
                    "pair_id": pair_id,
                    "debit_id": neg["id"],
                    "credit_id": pos["id"],
                    "amount": abs(neg["amount"]),
                })
                matched_ids.add(neg["id"])
                matched_ids.add(pos["id"])
                break

    # Mark transactions as transfers in state
    transfer_ids = matched_ids
    updated_transactions = []
    pair_map = {p["debit_id"]: p["pair_id"] for p in transfer_pairs}
    pair_map.update({p["credit_id"]: p["pair_id"] for p in transfer_pairs})

    for t in transactions:
        if t["id"] in transfer_ids:
            updated = dict(t)
            updated["is_transfer"] = True
            updated["transfer_pair_id"] = pair_map.get(t["id"])
            updated_transactions.append(updated)
        else:
            updated_transactions.append(t)

    return {
        "transactions": updated_transactions,
        "transfer_pairs": transfer_pairs,
    }
