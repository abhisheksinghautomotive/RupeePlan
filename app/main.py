from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.transactions import router as transactions_router

from contextlib import asynccontextmanager
from app.db.session import engine
from app.db.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="RupeePlan FinOps API",
    description="Backend for the RupeePlan Financial Operations system",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(transactions_router, prefix="/api/v1/transactions", tags=["Transactions"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "RupeePlan-Core"}

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to RupeePlan API"}
