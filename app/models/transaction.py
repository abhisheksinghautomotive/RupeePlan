from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Numeric, Text, Date, Boolean
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import date
from typing import Optional
from app.db.base import Base, TimestampMixin

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    category_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("categories.id"))
    
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Idempotency and Audit
    digest: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    raw_data: Mapped[Optional[str]] = mapped_column(Text)  # Original CSV row/line for audit
    is_analyzed: Mapped[bool] = mapped_column(default=False)

    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="transactions")
