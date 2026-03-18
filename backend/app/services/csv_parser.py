import pandas as pd
import io
from datetime import date
from typing import List, Dict, Any
from anthropic import Anthropic
from app.core.config import settings

client = Anthropic(api_key=settings.anthropic_api_key)

KNOWN_FORMATS = {
    "chase": {"date": "Transaction Date", "desc": "Description", "amount": "Amount"},
    "bofa": {"date": "Date", "desc": "Description", "amount": "Amount"},
    "amex": {"date": "Date", "desc": "Description", "amount": "Amount"},
    "wells_fargo": {"date": "Date", "desc": "Description", "amount": "Amount"},
}

def detect_and_normalize_csv(content: bytes, filename: str) -> List[Dict[str, Any]]:
    """Use LLM to normalize any CSV format into standard transactions."""
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise ValueError(f"Could not parse CSV: {e}")

    columns = list(df.columns)
    sample_rows = df.head(3).to_dict(orient="records")

    prompt = f"""You are a bank CSV parser. Given these column names and sample rows, identify:
1. Which column contains the transaction date
2. Which column contains the description/merchant
3. Which column contains the amount (negative = expense, positive = income)

Columns: {columns}
Sample rows: {sample_rows}

Respond in JSON format only:
{{"date_col": "column_name", "desc_col": "column_name", "amount_col": "column_name", "amount_sign_convention": "negative_expense|positive_expense"}}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    mapping = json.loads(response.content[0].text)

    transactions = []
    for _, row in df.iterrows():
        try:
            raw_amount = float(str(row[mapping["amount_col"]]).replace(",", "").replace("$", ""))
            # Normalize: negative = expense
            if mapping["amount_sign_convention"] == "positive_expense":
                raw_amount = -abs(raw_amount)

            transactions.append({
                "date": pd.to_datetime(row[mapping["date_col"]]).date(),
                "description": str(row[mapping["desc_col"]]),
                "amount": raw_amount,
            })
        except (ValueError, KeyError):
            continue

    return transactions


async def classify_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Batch classify transactions using LLM."""
    if not transactions:
        return transactions

    batch_text = "\n".join([
        f'{i}. "{t["description"]}" | ${t["amount"]}'
        for i, t in enumerate(transactions)
    ])

    prompt = f"""Classify each transaction into a category and clean the merchant name.
Categories: food_dining, groceries, rent_housing, transport, entertainment,
           subscriptions, healthcare, shopping, income, transfer, utilities, other

Transactions:
{batch_text}

Respond as JSON array with same order:
[{{"category": "...", "subcategory": "...", "merchant": "clean name", "is_recurring": bool}}]
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    text = response.content[0].text.strip()
    # Extract JSON array from response
    start = text.find("[")
    end = text.rfind("]") + 1
    classifications = json.loads(text[start:end])

    for i, classification in enumerate(classifications):
        if i < len(transactions):
            transactions[i].update(classification)

    return transactions
