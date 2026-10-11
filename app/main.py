from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router

app = FastAPI(
    title="Betting Calculation API",
    summary="Calculate betting rows and coupon statistics.",
    description=(
        "API for expanding betting selections into playable rows, applying "
        "odds-based filters, and calculating coupon-level statistics."
    ),
    version="1.0.0",
    openapi_tags=[
        {
            "name": "health",
            "description": "Service health and availability checks.",
        },
        {
            "name": "calculations",
            "description": (
                "Endpoints for reducing betting rows and calculating coupon data."
            ),
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
