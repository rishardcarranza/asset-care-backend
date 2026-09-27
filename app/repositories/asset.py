"""Asset repository for specialized asset queries and dynamic JSONB handling."""

from datetime import datetime
from typing import Sequence
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.repositories.base import BaseRepository
from app.schemas.asset import AssetCreate, AssetUpdate
from app.schemas.dynamic_metadata import validate_metadata_payload
from app.schemas.enums import AssetType


class AssetRepository(BaseRepository[Asset]):
    """Specialized repository for physical asset operations."""

    def __init__(self) -> None:
        super().__init__(Asset)

    def get_by_type(
        self, db: Session, *, asset_type: AssetType, skip: int = 0, limit: int = 100
    ) -> Sequence[Asset]:
        """Retrieve assets filtered by category."""
        stmt = (
            select(Asset)
            .where(Asset.asset_type == asset_type, Asset.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        return db.scalars(stmt).all()

    def get_modified_since(
        self, db: Session, *, since: datetime
    ) -> Sequence[Asset]:
        """Retrieve all assets modified or deleted since a specific timestamp.

        Intent:
            Powers incremental delta synchronization for offline-first clients.
            Includes soft-deleted records so clients can mirror deletions locally.
        """
        stmt = select(Asset).where(Asset.updated_at >= since)
        return db.scalars(stmt).all()

    def create_asset(self, db: Session, *, obj_in: AssetCreate) -> Asset:
        """Validate dynamic metadata schema and create a new asset record."""
        validated_metadata = validate_metadata_payload(
            obj_in.asset_type, obj_in.metadata_payload
        )

        db_obj = Asset(
            id=obj_in.id or uuid.uuid4(),
            name=obj_in.name,
            asset_type=obj_in.asset_type,
            description=obj_in.description,
            metadata_payload=validated_metadata,
        )
        return self.create(db, db_obj=db_obj)

    def update_asset(
        self, db: Session, *, db_obj: Asset, obj_in: AssetUpdate
    ) -> Asset:
        """Update asset properties and re-validate dynamic metadata if modified."""
        update_data = obj_in.model_dump(exclude_unset=True)

        target_type = obj_in.asset_type or db_obj.asset_type

        if "metadata_payload" in update_data and update_data["metadata_payload"] is not None:
            # Merge with existing metadata and re-validate
            merged = {**db_obj.metadata_payload, **update_data["metadata_payload"]}
            db_obj.metadata_payload = validate_metadata_payload(target_type, merged)

        if "name" in update_data and update_data["name"] is not None:
            db_obj.name = update_data["name"]
        if "asset_type" in update_data and update_data["asset_type"] is not None:
            db_obj.asset_type = update_data["asset_type"]
        if "description" in update_data:
            db_obj.description = update_data["description"]

        return self.update(db, db_obj=db_obj)


asset_repo = AssetRepository()
