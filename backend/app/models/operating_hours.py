"""Operating hours model for service locations."""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Time, Boolean, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class OperatingHours(Base):
    """Operating hours for a service at a location."""

    __tablename__ = "operating_hours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("service_locations.id", ondelete="CASCADE"), nullable=False)
    service_type_id = Column(Integer, ForeignKey("service_types.id", ondelete="CASCADE"))

    # Day of week (0 = Sunday, 6 = Saturday)
    day_of_week = Column(Integer, CheckConstraint("day_of_week >= 0 AND day_of_week <= 6"), nullable=False)

    # Time ranges (24-hour format)
    open_time = Column(Time)   # e.g., 08:00
    close_time = Column(Time)  # e.g., 17:00

    # Special cases
    is_24_hours = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)

    # Notes
    notes = Column(Text)  # e.g., "Last entry 30 min before closing"

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    location = relationship("ServiceLocation", back_populates="operating_hours")

    def __repr__(self):
        return f"<OperatingHours(location_id={self.location_id}, day={self.day_of_week}, {self.open_time}-{self.close_time})>"
