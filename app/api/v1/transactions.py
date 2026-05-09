from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from app.schemas.transaction import AsyncTaskResult, Transaction as TransactionSchema
from app.worker.tasks import process_csv_upload
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.account import Account

router = APIRouter()

@router.get("/accounts", response_model=List[dict]) # Simple dict for now or create a schema
async def list_accounts(
    db: AsyncSession = Depends(get_db)
):
    """
    List all accounts.
    """
    query = select(Account)
    result = await db.execute(query)
    accounts = result.scalars().all()
    return [{"id": a.id, "name": a.name, "institution": a.institution} for a in accounts]

@router.get("/", response_model=List[TransactionSchema])
async def list_transactions(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List transactions for a specific account.
    """
    query = select(Transaction).where(Transaction.account_id == account_id).offset(skip).limit(limit)
    result = await db.execute(query)
    transactions = result.scalars().all()
    return transactions

@router.post("/upload", response_model=AsyncTaskResult, status_code=202)
async def upload_statement(
    account_id: UUID = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a bank statement (CSV) for background processing.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        content = await file.read()
        # Decode bytes to string for Celery serialization
        content_str = content.decode("utf-8")
        
        # Trigger Celery Task
        task = process_csv_upload.delay(content_str, file.filename, str(account_id))
        
        return AsyncTaskResult(
            task_id=task.id,
            status="PENDING",
            message="CSV processing has started in the background"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error during task dispatch: {str(e)}")
