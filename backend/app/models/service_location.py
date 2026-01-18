"""Service location model."""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class ServiceLocation(Base):
    """Physical location offering one or more services."""

    __tablename__ = "service_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Basic Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    organization_name = Column(String(255))  # Parent org

    # Address
    street_address = Column(String(255))
    city = Column(String(100), default="New York")
    state = Column(String(2), default="NY")
    zip_code = Column(String(10))
    borough = Column(String(50))  # Manhattan, Brooklyn, Queens, Bronx, Staten Island

    # Geolocation (simple lat/lon columns instead of PostGIS)
    latitude = Column(Float)
    longitude = Column(Float)

    # Contact
    phone = Column(String(20))
    website = Column(String(500))
    email = Column(String(255))

    # Accessibility
    wheelchair_accessible = Column(Boolean)
    languages_spoken = Column(ARRAY(String))  # ['English', 'Spanish']

    # Metadata for scraper deduplication
    data_source = Column(String(100))  # e.g., "NYC Open Data", "Manual Entry"
    external_id = Column(String(255))  # External system ID
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))

    # Multi-city support
    city_code = Column(String(10), default="NYC")

    # Soft delete
    deleted_at = Column(DateTime(timezone=True))

    # Relationships for eager loading
    location_services = relationship("LocationService", back_populates="location", lazy="select")
    operating_hours = relationship("OperatingHours", back_populates="location", lazy="select")
    temporary_closures = relationship("TemporaryClosure", back_populates="location", lazy="select")

    def __repr__(self):
        return f"<ServiceLocation(id={self.id}, name='{self.name}', borough='{self.borough}')>"
