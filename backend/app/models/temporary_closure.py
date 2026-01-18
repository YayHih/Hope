"""Temporary closure and alert model."""
from sqlalchemy import Column, String, ForeignKey, DateTime, Date, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class TemporaryClosure(Base):
    """Temporary closures, schedule changes, and alerts for service locations."""

    __tablename__ = "temporary_closures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey("service_locations.id", ondelete="CASCADE"), nullable=False)

    # Closure period
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # NULL = indefinite closure

    # Details
    reason = Column(String(255))  # e.g., "Holiday", "Maintenance", "Weather"
    description = Column(Text)
    alert_type = Column(String(50), default="closure")  # 'closure', 'schedule_change', 'capacity_limit'

    # Priority for UI display
    is_urgent = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # Admin user

    # Active flag
    is_active = Column(Boolean, default=True)

    # Relationships
    location = relationship("ServiceLocation", back_populates="temporary_closures")

    def __repr__(self):
        return f"<TemporaryClosure(location_id={self.location_id}, start={self.start_date}, reason='{self.reason}')>"
