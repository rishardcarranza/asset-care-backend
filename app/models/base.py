"""Base SQLAlchemy declarative class and synchronization mixin."""

from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative root class for all SQLAlchemy 2.0 ORM models."""

    pass


class SyncBaseMixin:
    """Mixin providing offline-first synchronization metadata.

    Attributes:
        id: UUIDv4 primary key allowing offline entity creation on mobile without collisions.
        created_at: UTC timestamp when the record was initially created.
        updated_at: UTC timestamp of the latest change; updated on every modification.
        is_deleted: Soft-delete flag; critical for syncing deletions without data loss.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        index=True,
    )
