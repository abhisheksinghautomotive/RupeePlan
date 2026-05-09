import asyncio
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert
from app.worker.celery_app import celery_app
from app.services.parser import CSVParserService
from app.db.session import SessionLocal
from app.models.transaction import Transaction

async def save_transactions_to_db(account_id: str, parsed_data: list):
    """
    Performs a bulk upsert into PostgreSQL using 'ON CONFLICT DO NOTHING' 
    on the digest column to ensure idempotency.
    """
    if not parsed_data:
        return

    # Prepare the records for bulk insertion
    # Note: we use dictionaries for the PostgreSQL insert dialect
    stmt_values = [
        {
            "account_id": UUID(account_id),
            "transaction_date": record["date"],
            "amount": record["amount"],
            "description": record["description"],
            "digest": record["digest"],
            "raw_data": str(record["raw_data"]),
        }
        for record in parsed_data
    ]

    async with SessionLocal() as session:
        # PostgreSQL specific 'Upsert' logic
        # If the digest (hash) already exists, DO NOTHING
        stmt = insert(Transaction).values(stmt_values)
        on_conflict_stmt = stmt.on_conflict_do_nothing(index_elements=["digest"])
        
        await session.execute(on_conflict_stmt)
        await session.commit()

@celery_app.task(name="process_csv_upload")
def process_csv_upload(content: str, filename: str, account_id: str):
    """
    Celery task orchestration:
    1. Parse the CSV content into standardized records.
    2. Bulk insert records into the database with collision handling.
    """
    # Parse the content (content is passed as string from the API)
    result = CSVParserService.parse_statement(
        content=content.encode("utf-8"), 
        filename=filename, 
        account_id=account_id
    )
    
    if result["successful_records"] > 0:
        # Run the async database insertion within the Celery worker thread
        asyncio.run(save_transactions_to_db(account_id, result["data"]))
    
    return {
        "filename": filename,
        "processed": result["successful_records"],
        "failed": result["failed_records"]
    }
