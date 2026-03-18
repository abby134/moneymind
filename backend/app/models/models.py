import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Boolean, Date, Text, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ, JSONB
from app.core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    income_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow, onupdate=datetime.utcnow)

    bank_accounts: Mapped[list["BankAccount"]] = relationship(back_populates="user")
    monthly_snapshots: Mapped[list["MonthlySnapshot"]] = relationship(back_populates="user")
    goals: Mapped[list["Goal"]] = relationship(back_populates="user")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)  # checking/savings/credit
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="bank_accounts")
    csv_uploads: Mapped[list["CsvUpload"]] = relationship(back_populates="account")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="account")


class CsvUpload(Base):
    __tablename__ = "csv_uploads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    account_id: Mapped[str] = mapped_column(String, ForeignKey("bank_accounts.id"), nullable=False)
    month: Mapped[date] = mapped_column(Date, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="uploaded")  # uploaded/parsing/parsed/failed
    uploaded_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow)
    parsed_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)

    account: Mapped["BankAccount"] = relationship(back_populates="csv_uploads")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="upload")


class MonthlySnapshot(Base):
    __tablename__ = "monthly_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    month: Mapped[date] = mapped_column(Date, nullable=False)
    uploads_included: Mapped[int] = mapped_column(Integer, default=0)
    total_income: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_expenses: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    net_savings: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    savings_rate: Mapped[float] = mapped_column(Numeric(5, 4), default=0)
    net_worth_estimate: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    top_categories: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="monthly_snapshots")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="snapshot")
    goal_checkpoints: Mapped[list["GoalCheckpoint"]] = relationship(back_populates="snapshot")
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="snapshot")
    reports: Mapped[list["Report"]] = relationship(back_populates="snapshot")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    account_id: Mapped[str] = mapped_column(String, ForeignKey("bank_accounts.id"), nullable=False)
    upload_id: Mapped[str] = mapped_column(String, ForeignKey("csv_uploads.id"), nullable=False)
    snapshot_id: Mapped[str | None] = mapped_column(String, ForeignKey("monthly_snapshots.id"), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    is_transfer: Mapped[bool] = mapped_column(Boolean, default=False)
    transfer_pair_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow)

    account: Mapped["BankAccount"] = relationship(back_populates="transactions")
    upload: Mapped["CsvUpload"] = relationship(back_populates="transactions")
    snapshot: Mapped["MonthlySnapshot"] = relationship(back_populates="transactions")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    account_id: Mapped[str] = mapped_column(String, ForeignKey("bank_accounts.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly")
    first_detected: Mapped[date] = mapped_column(Date, nullable=False)
    last_seen: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/zombie/cancelled
    zombie_since: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="subscriptions")
    account: Mapped["BankAccount"] = relationship(back_populates="subscriptions")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    current_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/achieved/abandoned
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow)
    achieved_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)

    user: Mapped["User"] = relationship(back_populates="goals")
    checkpoints: Mapped[list["GoalCheckpoint"]] = relationship(back_populates="goal")


class GoalCheckpoint(Base):
    __tablename__ = "goal_checkpoints"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id"), nullable=False)
    snapshot_id: Mapped[str] = mapped_column(String, ForeignKey("monthly_snapshots.id"), nullable=False)
    amount_at_checkpoint: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    on_track: Mapped[bool] = mapped_column(Boolean, nullable=False)
    variance: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow)

    goal: Mapped["Goal"] = relationship(back_populates="checkpoints")
    snapshot: Mapped["MonthlySnapshot"] = relationship(back_populates="goal_checkpoints")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    snapshot_id: Mapped[str] = mapped_column(String, ForeignKey("monthly_snapshots.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/running/completed/failed
    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)
    agents_invoked: Mapped[list] = mapped_column(JSONB, default=list)
    fact_check_flags: Mapped[list] = mapped_column(JSONB, default=list)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    snapshot: Mapped["MonthlySnapshot"] = relationship(back_populates="agent_runs")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    snapshot_id: Mapped[str] = mapped_column(String, ForeignKey("monthly_snapshots.id"), nullable=False)
    agent_run_id: Mapped[str] = mapped_column(String, ForeignKey("agent_runs.id"), nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    email_sent_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)
    viewed_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=datetime.utcnow)

    snapshot: Mapped["MonthlySnapshot"] = relationship(back_populates="reports")
