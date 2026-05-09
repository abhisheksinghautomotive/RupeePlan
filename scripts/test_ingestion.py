import asyncio
from uuid import uuid4
from datetime import date
from decimal import Decimal
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.account import Account
from app.models.user import User
from app.worker.tasks import save_transactions_to_db

async def run_test():
    """
    Integration test script to verify:
    1. Database connection.
    2. Model creation.
    3. Idempotency (Upsert) logic in tasks.py.
    """
    print("🚀 Starting Integration Test...")
    
    # 1. Initialize DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as session:
        # 2. Setup mock data
        user_id = uuid4()
        account_id = uuid4()
        
        user = User(id=user_id, email=f"test_{uuid4().hex[:6]}@example.com", hashed_password="...")
        account = Account(
            id=account_id, 
            user_id=user_id, 
            name="Test Bank", 
            institution="HDFC", 
            account_type="SAVINGS", 
            currency="INR",
            balance=Decimal("0.00")
        )
        
        session.add(user)
        session.add(account)
        await session.commit()
        print(f"✅ Created test user and account: {account_id}")

        # 3. Prepare mock parsed data
        test_data = [
            {
                "date": date(2024, 5, 1),
                "amount": Decimal("1500.50"),
                "description": "Amazon Purchase",
                "digest": "unique_hash_1",
                "raw_data": {"Date": "2024-05-01", "Amount": "1500.50"}
            },
            {
                "date": date(2024, 5, 2),
                "amount": Decimal("-500.00"),
                "description": "ATM Withdrawal",
                "digest": "unique_hash_2",
                "raw_data": {"Date": "2024-05-02", "Amount": "-500.00"}
            }
        ]

        # 4. Run insertion (First time)
        print("📥 Running first insertion...")
        await save_transactions_to_db(str(account_id), test_data)
        
        # 5. Verify counts
        from sqlalchemy import select, func
        from app.models.transaction import Transaction
        
        count = await session.scalar(select(func.count()).select_from(Transaction))
        print(f"📊 Transaction count after first run: {count}")
        assert count == 2

        # 6. Run insertion (Second time - same data)
        # This tests the 'ON CONFLICT DO NOTHING' logic
        print("📥 Running second insertion (duplicates)...")
        await save_transactions_to_db(str(account_id), test_data)
        
        count = await session.scalar(select(func.count()).select_from(Transaction))
        print(f"📊 Transaction count after duplicate run: {count}")
        assert count == 2, "FAIL: Duplicate records were created!"
        
        print("✨ INTEGRATION TEST PASSED: Idempotency is working at the DB level.")

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
