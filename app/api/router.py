from fastapi import APIRouter
from app.api.v1 import health, domains, generate, export

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(domains.router)
api_router.include_router(generate.router)
api_router.include_router(export.router)
