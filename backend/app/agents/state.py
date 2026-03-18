from typing import TypedDict, Annotated, List, Optional
from datetime import date
import operator


class Transaction(TypedDict):
    id: str
    date: str
    description: str
    amount: float
    category: str
    merchant: str
    is_transfer: bool
    account_id: str


class PatternInsight(TypedDict):
    type: str
    description: str
    supporting_months: List[str]
    confidence: float
    source_verified: bool


class AgentState(TypedDict):
    user_id: str
    snapshot_id: str
    month: str  # "2025-03"
    transactions: List[Transaction]
    memory_context: str  # Retrieved from Memory MCP

    # Worker outputs (populated in parallel)
    pattern_insights: Annotated[List[PatternInsight], operator.add]
    anomalies: Annotated[List[dict], operator.add]
    goal_updates: Annotated[List[dict], operator.add]
    subscription_updates: Annotated[List[dict], operator.add]
    transfer_pairs: Annotated[List[dict], operator.add]

    # Validation
    fact_check_flags: List[dict]
    verified_insights: List[dict]

    # Output
    report_md: Optional[str]
    memory_updates: List[dict]
    errors: Annotated[List[str], operator.add]
