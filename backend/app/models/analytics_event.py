"""Anonymous analytics event model - privacy-safe."""
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database import Base


class AnalyticsEvent(Base):
    """Anonymous analytics events (aggregate only, no PII)."""

    __tablename__ = "analytics_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Event type
    event_type = Column(String(50), nullable=False)  # 'map_view', 'location_click', 'filter_applied'

    # Anonymous context (ephemeral session ID with 24h TTL)
    session_hash = Column(String(64))

    # Location context (for popular services tracking)
    location_id = Column(UUID(as_uuid=True), ForeignKey("service_locations.id", ondelete="SET NULL"))
    service_type_id = Column(Integer, ForeignKey("service_types.id", ondelete="SET NULL"))

    # Geographic aggregation (borough level ONLY, NOT precise GPS)
    borough = Column(String(50))

    # Additional event data
    event_data = Column(JSONB)  # e.g., {"filter": "open_now", "distance_km": 2}

    def __repr__(self):
        return f"<AnalyticsEvent(id={self.id}, event_type='{self.event_type}', borough='{self.borough}')>"
