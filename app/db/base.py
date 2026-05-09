from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()
    )

# Models should be imported explicitly where needed for Base.metadata to pick them up
# (e.g., in Alembic env.py or in the application entry point)
