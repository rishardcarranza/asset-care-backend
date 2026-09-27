"""Offline-First synchronization endpoints for mobile client."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.models.maintenance_log import MaintenanceLog
from app.models.maintenance_rule import MaintenanceRule
from app.repositories.asset import asset_repo
from app.repositories.maintenance import log_repo, rule_repo
from app.schemas.dynamic_metadata import validate_metadata_payload
from app.schemas.sync import (
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
)

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.get("/pull", response_model=SyncPullResponse)
def sync_pull(
    since: datetime = Query(
        ...,
        description="UTC timestamp of the client's last successful synchronization",
    ),
    db: Session = Depends(get_db),
) -> SyncPullResponse:
    """Deliver all assets, rules, and logs modified or deleted since the provided timestamp.

    Intent:
        Enables incremental delta downloads. Soft-deleted records are included
        so the mobile SQLite database can apply local deletions.
    """
    now_utc = datetime.now(timezone.utc)
    assets = asset_repo.get_modified_since(db, since=since)
    rules = rule_repo.get_modified_since(db, since=since)
    logs = log_repo.get_modified_since(db, since=since)

    return SyncPullResponse(
        synced_at=now_utc,
        assets=list(assets),
        maintenance_rules=list(rules),
        maintenance_logs=list(logs),
    )


@router.post("/push", response_model=SyncPushResponse)
def sync_push(
    payload: SyncPushRequest,
    db: Session = Depends(get_db),
) -> SyncPushResponse:
    """Reconcile offline-created or modified mutations using Last-Write-Wins strategy.

    Intent:
        Processes mutations submitted by the client while disconnected.
        Uses client-generated UUIDs to ensure seamless identity persistence across SQLite and PostgreSQL.
    """
    now_utc = datetime.now(timezone.utc)
    applied_assets = 0
    applied_rules = 0
    applied_logs = 0

    # 1. Process Asset Mutations
    for item in payload.assets:
        existing = db.get(Asset, item.id)
        validated_meta = validate_metadata_payload(item.asset_type, item.metadata_payload)
        if existing:
            # Last-Write-Wins: Apply if incoming update is newer or server allows
            existing.name = item.name
            existing.asset_type = item.asset_type
            existing.description = item.description
            existing.metadata_payload = validated_meta
            existing.is_deleted = item.is_deleted
            existing.updated_at = now_utc
            db.add(existing)
        else:
            new_asset = Asset(
                id=item.id,
                name=item.name,
                asset_type=item.asset_type,
                description=item.description,
                metadata_payload=validated_meta,
                is_deleted=item.is_deleted,
                updated_at=now_utc,
            )
            db.add(new_asset)
        applied_assets += 1

    # 2. Process Maintenance Rule Mutations
    for r_item in payload.maintenance_rules:
        existing_rule = db.get(MaintenanceRule, r_item.id)
        if existing_rule:
            existing_rule.maintenance_type = r_item.maintenance_type
            existing_rule.metric_type = r_item.metric_type
            existing_rule.interval_value = r_item.interval_value
            existing_rule.metric_unit = r_item.metric_unit
            existing_rule.description = r_item.description
            existing_rule.is_deleted = r_item.is_deleted
            existing_rule.updated_at = now_utc
            db.add(existing_rule)
        else:
            new_rule = MaintenanceRule(
                id=r_item.id,
                asset_id=r_item.asset_id,
                maintenance_type=r_item.maintenance_type,
                metric_type=r_item.metric_type,
                interval_value=r_item.interval_value,
                metric_unit=r_item.metric_unit,
                description=r_item.description,
                is_deleted=r_item.is_deleted,
                updated_at=now_utc,
            )
            db.add(new_rule)
        applied_rules += 1

    # 3. Process Maintenance Log Mutations
    for l_item in payload.maintenance_logs:
        existing_log = db.get(MaintenanceLog, l_item.id)
        if existing_log:
            existing_log.maintenance_type = l_item.maintenance_type
            existing_log.service_date = l_item.service_date
            existing_log.metric_value_at_service = l_item.metric_value_at_service
            existing_log.cost = l_item.cost
            existing_log.notes = l_item.notes
            existing_log.performed_by = l_item.performed_by
            existing_log.is_deleted = l_item.is_deleted
            existing_log.updated_at = now_utc
            db.add(existing_log)
        else:
            new_log = MaintenanceLog(
                id=l_item.id,
                asset_id=l_item.asset_id,
                maintenance_type=l_item.maintenance_type,
                service_date=l_item.service_date,
                metric_value_at_service=l_item.metric_value_at_service,
                cost=l_item.cost,
                notes=l_item.notes,
                performed_by=l_item.performed_by,
                is_deleted=l_item.is_deleted,
                updated_at=now_utc,
            )
            db.add(new_log)
        applied_logs += 1

    db.commit()

    return SyncPushResponse(
        synced_at=now_utc,
        applied_assets=applied_assets,
        applied_rules=applied_rules,
        applied_logs=applied_logs,
    )
