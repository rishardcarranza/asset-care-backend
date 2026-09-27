"""Generic BaseRepository providing type-safe CRUD operations with soft-delete."""

from typing import Generic, Sequence, TypeVar
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository encapsulating common database queries.

    Intent:
        By enforcing soft-delete checks (is_deleted == False) in standard lookups,
        we prevent queries from returning discarded records while preserving tombstone
        records for offline synchronization clients.
    """

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, id: uuid.UUID) -> ModelType | None:
        """Fetch a single active record by UUID."""
        stmt = select(self.model).where(
            self.model.id == id,
            self.model.is_deleted.is_(False),
        )
        return db.scalar(stmt)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """Fetch a paginated list of active records."""
        stmt = (
            select(self.model)
            .where(self.model.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        return db.scalars(stmt).all()

    def create(self, db: Session, *, db_obj: ModelType) -> ModelType:
        """Persist a new entity instance."""
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType) -> ModelType:
        """Commit updates to an existing attached entity."""
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_soft(self, db: Session, *, id: uuid.UUID) -> ModelType | None:
        """Mark a record as deleted without physical row destruction.

        Intent:
            Physical deletion breaks synchronization for offline clients that haven't
            pulled yet. Soft-deletion allows the server to notify clients to delete locally.
        """
        db_obj = self.get(db, id)
        if db_obj:
            db_obj.is_deleted = True
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
