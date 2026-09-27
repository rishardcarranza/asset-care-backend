"""Maintenance rule and log endpoints."""

from typing import Sequence
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.asset import asset_repo
from app.repositories.maintenance import log_repo, rule_repo
from app.schemas.maintenance_log import (
    MaintenanceLogCreate,
    MaintenanceLogResponse,
)
from app.schemas.maintenance_rule import (
    MaintenanceRuleCreate,
    MaintenanceRuleResponse,
)

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


# ==========================================
# Maintenance Rules (Preventive Thresholds)
# ==========================================

@router.post("/rules", response_model=MaintenanceRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_in: MaintenanceRuleCreate,
    db: Session = Depends(get_db),
) -> MaintenanceRuleResponse:
    """Create a new preventive maintenance threshold rule for an asset."""
    asset = asset_repo.get(db, id=rule_in.asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ASSET_NOT_FOUND", "message": f"Asset {rule_in.asset_id} not found."},
        )
    return rule_repo.create_rule(db, obj_in=rule_in)


@router.get("/rules/asset/{asset_id}", response_model=list[MaintenanceRuleResponse])
def get_rules_for_asset(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Sequence[MaintenanceRuleResponse]:
    """Retrieve all active maintenance rules configured for an asset."""
    return rule_repo.get_by_asset(db, asset_id=asset_id)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """Soft-delete a maintenance rule."""
    deleted = rule_repo.delete_soft(db, id=rule_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RULE_NOT_FOUND", "message": f"Rule {rule_id} not found."},
        )


# ==========================================
# Maintenance Logs (Execution History)
# ==========================================

@router.post("/logs", response_model=MaintenanceLogResponse, status_code=status.HTTP_201_CREATED)
def record_service_log(
    log_in: MaintenanceLogCreate,
    db: Session = Depends(get_db),
) -> MaintenanceLogResponse:
    """Record an executed maintenance service log for an asset."""
    asset = asset_repo.get(db, id=log_in.asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ASSET_NOT_FOUND", "message": f"Asset {log_in.asset_id} not found."},
        )

    # Optionally update asset's last_odometer if log has a higher reading
    if log_in.metric_value_at_service is not None:
        current_odometer = float(asset.metadata_payload.get("last_odometer", 0.0))
        if log_in.metric_value_at_service > current_odometer:
            asset.metadata_payload["last_odometer"] = log_in.metric_value_at_service
            # Flag modified so SQLAlchemy commits the JSONB change
            asset_repo.update(db, db_obj=asset)

    return log_repo.create_log(db, obj_in=log_in)


@router.get("/logs/asset/{asset_id}", response_model=list[MaintenanceLogResponse])
def get_logs_for_asset(
    asset_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
) -> Sequence[MaintenanceLogResponse]:
    """Retrieve service history for an asset, ordered by service date descending."""
    return log_repo.get_by_asset(db, asset_id=asset_id, skip=skip, limit=limit)


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    """Soft-delete a maintenance service log."""
    deleted = log_repo.delete_soft(db, id=log_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "LOG_NOT_FOUND", "message": f"Log {log_id} not found."},
        )
