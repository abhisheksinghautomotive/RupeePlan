from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID
from typing import Optional, List
from decimal import Decimal

class TransactionBase(BaseModel):
    date: date
    amount: Decimal
    description: str
    category_id: Optional[UUID] = None
    account_id: UUID

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: UUID

    class Config:
        from_attributes = True

class CSVParseResult(BaseModel):
    filename: str
    total_records: int
    successful_records: int
    failed_records: int
    errors: List[str] = []

class AsyncTaskResult(BaseModel):
    task_id: str
    status: str
    message: str
