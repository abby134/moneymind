from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional

# Auth
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: str
    email: str
    name: str
    timezone: str
    model_config = {"from_attributes": True}

# Bank Accounts
class BankAccountCreate(BaseModel):
    nickname: str
    bank_name: str
    account_type: str
    currency: str = "USD"

class BankAccountOut(BaseModel):
    id: str
    nickname: str
    bank_name: str
    account_type: str
    currency: str
    is_active: bool
    model_config = {"from_attributes": True}

# Uploads
class CsvUploadOut(BaseModel):
    id: str
    account_id: str
    month: date
    original_filename: str
    row_count: Optional[int]
    status: str
    uploaded_at: datetime
    model_config = {"from_attributes": True}

# Snapshots
class MonthlySnapshotOut(BaseModel):
    id: str
    month: date
    uploads_included: int
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    top_categories: dict
    is_complete: bool
    model_config = {"from_attributes": True}

# Goals
class GoalCreate(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0
    target_date: date

class GoalUpdate(BaseModel):
    current_amount: Optional[float] = None
    status: Optional[str] = None

class GoalCheckpointOut(BaseModel):
    id: str
    amount_at_checkpoint: float
    on_track: bool
    variance: float
    recorded_at: datetime
    model_config = {"from_attributes": True}

class GoalOut(BaseModel):
    id: str
    name: str
    target_amount: float
    current_amount: float
    target_date: date
    status: str
    created_at: datetime
    achieved_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class GoalWithCheckpoints(GoalOut):
    checkpoints: list[GoalCheckpointOut] = []

# Reports
class ReportOut(BaseModel):
    id: str
    snapshot_id: str
    content_md: str
    created_at: datetime
    model_config = {"from_attributes": True}

# Agent Run
class AgentRunOut(BaseModel):
    id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    agents_invoked: list
    fact_check_flags: list
    model_config = {"from_attributes": True}
