from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Goal, GoalCheckpoint
from app.schemas.schemas import GoalCreate, GoalOut, GoalWithCheckpoints, GoalUpdate, GoalCheckpointOut
import uuid

router = APIRouter()


@router.get("/", response_model=list[GoalWithCheckpoints])
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Goal)
        .where(Goal.user_id == current_user.id)
        .order_by(Goal.created_at.desc())
    )
    goals = result.scalars().all()

    out = []
    for goal in goals:
        cp_result = await db.execute(
            select(GoalCheckpoint)
            .where(GoalCheckpoint.goal_id == goal.id)
            .order_by(GoalCheckpoint.recorded_at.desc())
        )
        checkpoints = cp_result.scalars().all()
        out.append(GoalWithCheckpoints(
            id=goal.id,
            name=goal.name,
            target_amount=float(goal.target_amount),
            current_amount=float(goal.current_amount),
            target_date=goal.target_date,
            status=goal.status,
            created_at=goal.created_at,
            achieved_at=goal.achieved_at,
            checkpoints=[
                GoalCheckpointOut(
                    id=c.id,
                    amount_at_checkpoint=float(c.amount_at_checkpoint),
                    on_track=c.on_track,
                    variance=float(c.variance),
                    recorded_at=c.recorded_at,
                )
                for c in checkpoints
            ],
        ))
    return out


@router.post("/", response_model=GoalOut)
async def create_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = Goal(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=data.name,
        target_amount=data.target_amount,
        current_amount=data.current_amount,
        target_date=data.target_date,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


@router.patch("/{goal_id}", response_model=GoalOut)
async def update_goal(
    goal_id: str,
    data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if data.current_amount is not None:
        goal.current_amount = data.current_amount
        if data.current_amount >= float(goal.target_amount):
            goal.status = "achieved"
            from datetime import datetime
            goal.achieved_at = datetime.utcnow()

    if data.status is not None:
        goal.status = data.status

    await db.commit()
    await db.refresh(goal)
    return goal


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.status = "abandoned"
    await db.commit()
    return {"ok": True}
