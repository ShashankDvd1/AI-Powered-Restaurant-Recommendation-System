from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import health, recommendations
from src.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Zomato AI Restaurant Recommendations",
    description="AI-powered restaurant recommendations using structured filters and Grok.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(recommendations.router)
