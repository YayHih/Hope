"""Many-to-many relationship between locations and service types."""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class LocationService(Base):
    """Association table linking service locations to service types."""

    __tablename__ = "location_services"

    location_id = Column(UUID(as_uuid=True), ForeignKey("service_locations.id", ondelete="CASCADE"), primary_key=True)
    service_type_id = Column(Integer, ForeignKey("service_types.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Service-specific details
    notes = Column(Text)  # e.g., "ID required", "Men only", "Ages 18+"
    capacity = Column(Integer)  # Optional capacity information

    # Relationships
    location = relationship("ServiceLocation", back_populates="location_services")
    service_type = relationship("ServiceType", back_populates="location_services")

    def __repr__(self):
        return f"<LocationService(location_id={self.location_id}, service_type_id={self.service_type_id})>"
