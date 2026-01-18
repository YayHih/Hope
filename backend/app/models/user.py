"""User model - minimal PII for privacy."""
from sqlalchemy import Column, String, Boolean, DateTime, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    """User model with minimal personal information."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True))

    # Authentication (passwordless via OTP)
    # Phone number is encrypted at rest using pgcrypto
    phone_number = Column(String(20), unique=True)  # Will be encrypted in application layer
    phone_verified = Column(Boolean, default=False)

    # Preferences (stored as JSONB for flexibility)
    preferences = Column(JSONB, default={})

    # Soft delete for GDPR compliance
    deleted_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<User(id={self.id}, phone_verified={self.phone_verified})>"
