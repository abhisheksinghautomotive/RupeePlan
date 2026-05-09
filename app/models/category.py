from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from uuid import UUID, uuid4
from typing import List, Optional
from app.db.base import Base, TimestampMixin

class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="category")
    budgets: Mapped[List["Budget"]] = relationship("Budget", back_populates="category")
