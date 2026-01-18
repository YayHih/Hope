"""User favorites model."""
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class UserFavorite(Base):
    """User's favorite service locations (optional feature)."""

    __tablename__ = "user_favorites"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("service_locations.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<UserFavorite(user_id={self.user_id}, location_id={self.location_id})>"
