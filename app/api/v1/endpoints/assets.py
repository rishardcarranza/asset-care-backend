"""Asset endpoints for Asset Care API."""

from typing import Sequence
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.asset import asset_repo
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from app.schemas.enums import AssetType
from app.schemas.health import AssetHealthReport
from app.services.maintenance_scheduler import scheduler_service

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("/", response_model=list[AssetResponse])
def list_assets(
    asset_type: AssetType | None = Query(default=None, description="Filter by asset category"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
) -> Sequence[AssetResponse]:
    """List active physical assets with optional category filtering and pagination."""
    if asset_type:
        return asset_repo.get_by_type(db, asset_type=asset_type, skip=skip, limit=limit)
    return asset_repo.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
) -> AssetResponse:
    """Create a new asset with dynamic JSONB metadata validation.

    Accepts an optional client-generated UUID for offline-first creation.
    """
    return asset_repo.create_asset(db, obj_in=asset_in)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> AssetResponse:
    """Retrieve an asset by its UUID."""
    asset = asset_repo.get(db, id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ASSET_NOT_FOUND", "message": f"Asset {asset_id} not found."},
        )
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: uuid.UUID,
    asset_in: AssetUpdate,
    db: Session = Depends(get_db),
) -> AssetResponse:
    """Update asset fields and re-validate dynamic telemetry/metadata."""
    db_obj = asset_repo.get(db, id=asset_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ASSET_NOT_FOUND", "message": f"Asset {asset_id} not found."},
        )
    return asset_repo.update_asset(db, db_obj=db_obj, obj_in=asset_in)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """Soft-delete an asset, preserving tombstone for offline sync replication."""
    deleted = asset_repo.delete_soft(db, id=asset_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ASSET_NOT_FOUND", "message": f"Asset {asset_id} not found."},
        )


@router.get("/{asset_id}/health", response_model=AssetHealthReport)
def get_asset_health(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> AssetHealthReport:
    """Compute and return preventive maintenance health status across all configured rules."""
    asset = asset_repo.get(db, id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ASSET_NOT_FOUND", "message": f"Asset {asset_id} not found."},
        )
    return scheduler_service.evaluate_asset_health(db, asset=asset)
