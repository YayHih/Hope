"""Service type model (Food, Shelter, etc.)."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ServiceType(Base):
    """Service type categorization (food, shelter, hygiene, etc.)."""

    __tablename__ = "service_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Food"
    slug = Column(String(100), nullable=False, unique=True)  # e.g., "food"
    description = Column(Text)
    icon_name = Column(String(50))  # For mobile app icons
    color_hex = Column(String(7))   # For map markers (e.g., "#FF6B6B")
    sort_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    location_services = relationship("LocationService", back_populates="service_type")

    def __repr__(self):
        return f"<ServiceType(id={self.id}, name='{self.name}', slug='{self.slug}')>"
