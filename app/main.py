from fastapi import FastAPI

app = FastAPI(
    title="RupeePlan FinOps API",
    description="Backend for the RupeePlan Financial Operations system",
    version="0.1.0"
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "RupeePlan-Core"}

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to RupeePlan API"}
