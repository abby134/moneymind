from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, BankAccount, CsvUpload, Transaction, MonthlySnapshot
from app.schemas.schemas import CsvUploadOut
from app.services.csv_parser import detect_and_normalize_csv, classify_transactions
import uuid

router = APIRouter()


async def process_csv_background(upload_id: str, content: bytes, user_id: str, account_id: str, month: date):
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(CsvUpload).where(CsvUpload.id == upload_id))
        upload = result.scalar_one()

        try:
            upload.status = "parsing"
            await db.commit()

            transactions = detect_and_normalize_csv(content, upload.original_filename)
            transactions = await classify_transactions(transactions)

            # Get or create monthly snapshot
            snap_result = await db.execute(
                select(MonthlySnapshot).where(
                    MonthlySnapshot.user_id == user_id,
                    MonthlySnapshot.month == month,
                )
            )
            snapshot = snap_result.scalar_one_or_none()
            if not snapshot:
                snapshot = MonthlySnapshot(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    month=month,
                )
                db.add(snapshot)
                await db.flush()

            for t in transactions:
                txn = Transaction(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    account_id=account_id,
                    upload_id=upload_id,
                    snapshot_id=snapshot.id,
                    date=t["date"],
                    description=t["description"],
                    amount=t["amount"],
                    category=t.get("category"),
                    subcategory=t.get("subcategory"),
                    merchant=t.get("merchant"),
                    is_recurring=t.get("is_recurring", False),
                )
                db.add(txn)

            upload.status = "parsed"
            upload.row_count = len(transactions)
            snapshot.uploads_included += 1

            await db.commit()
        except Exception as e:
            upload.status = "failed"
            await db.commit()
            raise


@router.post("/", response_model=CsvUploadOut)
async def upload_csv(
    background_tasks: BackgroundTasks,
    account_id: str = Form(...),
    month: date = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify account belongs to user
    result = await db.execute(
        select(BankAccount).where(BankAccount.id == account_id, BankAccount.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Account not found")

    content = await file.read()

    upload = CsvUpload(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        account_id=account_id,
        month=month,
        original_filename=file.filename,
        status="uploaded",
    )
    db.add(upload)
    await db.commit()
    await db.refresh(upload)

    background_tasks.add_task(
        process_csv_background,
        upload.id,
        content,
        current_user.id,
        account_id,
        month,
    )

    return upload
