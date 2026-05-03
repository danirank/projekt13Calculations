from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI(
    title="Betting Calculation API",
    description="API for calculating betting odds and reductions based on match data and user selections.",
    version="1.0.0"
)

app.include_router(router, prefix="/api")


