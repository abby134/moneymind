from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, MonthlySnapshot, Transaction, AgentRun, Report
from app.schemas.schemas import MonthlySnapshotOut, AgentRunOut
from app.agents.pipeline import pipeline
from app.agents.state import AgentState
import uuid

router = APIRouter()


@router.get("/", response_model=list[MonthlySnapshotOut])
async def list_snapshots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MonthlySnapshot)
        .where(MonthlySnapshot.user_id == current_user.id)
        .order_by(MonthlySnapshot.month.desc())
    )
    return result.scalars().all()


async def run_agent_pipeline(snapshot_id: str, user_id: str):
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        snap_result = await db.execute(select(MonthlySnapshot).where(MonthlySnapshot.id == snapshot_id))
        snapshot = snap_result.scalar_one()

        txn_result = await db.execute(
            select(Transaction).where(Transaction.snapshot_id == snapshot_id)
        )
        transactions = txn_result.scalars().all()

        run = AgentRun(
            id=str(uuid.uuid4()),
            user_id=user_id,
            snapshot_id=snapshot_id,
            status="running",
        )
        db.add(run)
        await db.commit()

        try:
            state = AgentState(
                user_id=user_id,
                snapshot_id=snapshot_id,
                month=snapshot.month.strftime("%Y-%m"),
                transactions=[{
                    "id": t.id,
                    "date": str(t.date),
                    "description": t.description,
                    "amount": float(t.amount),
                    "category": t.category or "other",
                    "merchant": t.merchant or t.description,
                    "is_transfer": t.is_transfer,
                    "account_id": t.account_id,
                } for t in transactions],
                memory_context="",
                pattern_insights=[],
                anomalies=[],
                goal_updates=[],
                subscription_updates=[],
                transfer_pairs=[],
                fact_check_flags=[],
                verified_insights=[],
                report_md=None,
                memory_updates=[],
                errors=[],
            )

            result = await pipeline.ainvoke(state)

            # Recompute financials excluding transfers
            non_transfer_txns = [t for t in result["transactions"] if not t.get("is_transfer")]
            total_income = sum(t["amount"] for t in non_transfer_txns if t["amount"] > 0)
            total_expenses = sum(abs(t["amount"]) for t in non_transfer_txns if t["amount"] < 0)
            net_savings = total_income - total_expenses

            category_totals: dict[str, float] = {}
            for t in non_transfer_txns:
                if t["amount"] < 0:
                    cat = t.get("category", "other")
                    category_totals[cat] = category_totals.get(cat, 0) + abs(t["amount"])

            snapshot.total_income = total_income
            snapshot.total_expenses = total_expenses
            snapshot.net_savings = net_savings
            snapshot.savings_rate = net_savings / total_income if total_income > 0 else 0
            snapshot.top_categories = category_totals
            snapshot.is_complete = True

            run.status = "completed"
            run.agents_invoked = ["planner", "transfer_detector", "pattern", "anomaly", "goal", "subscription", "fact_checker", "writer"]
            run.fact_check_flags = result.get("fact_check_flags", [])

            if result.get("report_md"):
                report = Report(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    snapshot_id=snapshot_id,
                    agent_run_id=run.id,
                    content_md=result["report_md"],
                )
                db.add(report)

            await db.commit()
        except Exception as e:
            run.status = "failed"
            run.error_message = str(e)
            await db.commit()


@router.post("/{snapshot_id}/analyze", response_model=AgentRunOut)
async def trigger_analysis(
    snapshot_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MonthlySnapshot).where(
            MonthlySnapshot.id == snapshot_id,
            MonthlySnapshot.user_id == current_user.id,
        )
    )
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    run = AgentRun(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        snapshot_id=snapshot_id,
        status="pending",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    background_tasks.add_task(run_agent_pipeline, snapshot_id, current_user.id)

    return run
