from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, BankAccount
from app.schemas.schemas import BankAccountCreate, BankAccountOut
import uuid

router = APIRouter()


@router.get("/", response_model=list[BankAccountOut])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankAccount).where(BankAccount.user_id == current_user.id, BankAccount.is_active == True)
    )
    return result.scalars().all()


@router.post("/", response_model=BankAccountOut)
async def create_account(
    data: BankAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = BankAccount(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **data.model_dump(),
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankAccount).where(BankAccount.id == account_id, BankAccount.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.is_active = False
    await db.commit()
    return {"ok": True}
