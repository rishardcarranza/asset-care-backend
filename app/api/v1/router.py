"""Aggregated API v1 router combining all resource endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import assets, maintenance, sync

api_router = APIRouter()

api_router.include_router(assets.router)
api_router.include_router(maintenance.router)
api_router.include_router(sync.router)
