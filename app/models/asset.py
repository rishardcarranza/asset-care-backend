"""Asset ORM model."""

from typing import TYPE_CHECKING, Any
from sqlalchemy import Enum as SQLEnum, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SyncBaseMixin
from app.schemas.enums import AssetType

if TYPE_CHECKING:
    from app.models.maintenance_log import MaintenanceLog
    from app.models.maintenance_rule import MaintenanceRule


class Asset(Base, SyncBaseMixin):
    """Core physical asset entity with dynamic JSONB metadata."""

    __tablename__ = "assets"

    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    asset_type: Mapped[AssetType] = mapped_column(
        SQLEnum(AssetType, name="asset_type_enum"),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Dynamic JSONB storage for category-specific attributes (e.g. engine, btu, warranty)
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Relationships
    rules: Mapped[list["MaintenanceRule"]] = relationship(
        "MaintenanceRule",
        back_populates="asset",
        cascade="all, delete-orphan",
        order_by="MaintenanceRule.created_at",
    )
    logs: Mapped[list["MaintenanceLog"]] = relationship(
        "MaintenanceLog",
        back_populates="asset",
        cascade="all, delete-orphan",
        order_by="desc(MaintenanceLog.service_date)",
    )
