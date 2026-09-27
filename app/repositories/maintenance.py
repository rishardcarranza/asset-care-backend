"""Repositories for maintenance rules and service logs."""

from datetime import datetime
from typing import Sequence
import uuid

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.maintenance_log import MaintenanceLog
from app.models.maintenance_rule import MaintenanceRule
from app.repositories.base import BaseRepository
from app.schemas.maintenance_log import MaintenanceLogCreate
from app.schemas.maintenance_rule import MaintenanceRuleCreate


class MaintenanceRuleRepository(BaseRepository[MaintenanceRule]):
    """Repository handling preventive maintenance interval rules."""

    def __init__(self) -> None:
        super().__init__(MaintenanceRule)

    def get_by_asset(
        self, db: Session, *, asset_id: uuid.UUID
    ) -> Sequence[MaintenanceRule]:
        """Fetch all active rules for an asset."""
        stmt = (
            select(MaintenanceRule)
            .where(
                MaintenanceRule.asset_id == asset_id,
                MaintenanceRule.is_deleted.is_(False),
            )
            .order_by(MaintenanceRule.created_at)
        )
        return db.scalars(stmt).all()

    def get_modified_since(
        self, db: Session, *, since: datetime
    ) -> Sequence[MaintenanceRule]:
        """Fetch rules changed since timestamp for sync pull."""
        stmt = select(MaintenanceRule).where(MaintenanceRule.updated_at >= since)
        return db.scalars(stmt).all()

    def create_rule(
        self, db: Session, *, obj_in: MaintenanceRuleCreate
    ) -> MaintenanceRule:
        """Create a new maintenance rule with optional client UUID."""
        db_obj = MaintenanceRule(
            id=obj_in.id or uuid.uuid4(),
            asset_id=obj_in.asset_id,
            maintenance_type=obj_in.maintenance_type,
            metric_type=obj_in.metric_type,
            interval_value=obj_in.interval_value,
            metric_unit=obj_in.metric_unit,
            description=obj_in.description,
        )
        return self.create(db, db_obj=db_obj)


class MaintenanceLogRepository(BaseRepository[MaintenanceLog]):
    """Repository handling executed maintenance service logs."""

    def __init__(self) -> None:
        super().__init__(MaintenanceLog)

    def get_by_asset(
        self, db: Session, *, asset_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[MaintenanceLog]:
        """Fetch service history for an asset, ordered by date descending."""
        stmt = (
            select(MaintenanceLog)
            .where(
                MaintenanceLog.asset_id == asset_id,
                MaintenanceLog.is_deleted.is_(False),
            )
            .order_by(desc(MaintenanceLog.service_date))
            .offset(skip)
            .limit(limit)
        )
        return db.scalars(stmt).all()

    def get_latest_for_type(
        self, db: Session, *, asset_id: uuid.UUID, maintenance_type: str
    ) -> MaintenanceLog | None:
        """Fetch the most recent service log for a specific maintenance type."""
        stmt = (
            select(MaintenanceLog)
            .where(
                MaintenanceLog.asset_id == asset_id,
                MaintenanceLog.maintenance_type == maintenance_type,
                MaintenanceLog.is_deleted.is_(False),
            )
            .order_by(desc(MaintenanceLog.service_date))
            .limit(1)
        )
        return db.scalar(stmt)

    def get_modified_since(
        self, db: Session, *, since: datetime
    ) -> Sequence[MaintenanceLog]:
        """Fetch logs changed since timestamp for sync pull."""
        stmt = select(MaintenanceLog).where(MaintenanceLog.updated_at >= since)
        return db.scalars(stmt).all()

    def create_log(
        self, db: Session, *, obj_in: MaintenanceLogCreate
    ) -> MaintenanceLog:
        """Create a service log entry with optional client UUID."""
        db_obj = MaintenanceLog(
            id=obj_in.id or uuid.uuid4(),
            asset_id=obj_in.asset_id,
            maintenance_type=obj_in.maintenance_type,
            service_date=obj_in.service_date,
            metric_value_at_service=obj_in.metric_value_at_service,
            cost=obj_in.cost,
            notes=obj_in.notes,
            performed_by=obj_in.performed_by,
        )
        return self.create(db, db_obj=db_obj)


rule_repo = MaintenanceRuleRepository()
log_repo = MaintenanceLogRepository()
