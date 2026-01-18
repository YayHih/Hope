"""Simple schema without PostGIS

Revision ID: 002
Revises:
Create Date: 2026-01-06 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions (no PostGIS needed)
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column('phone_number', sa.String(20), unique=True),
        sa.Column('phone_verified', sa.Boolean(), default=False),
        sa.Column('preferences', postgresql.JSONB, default={}),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )
    op.create_index('idx_users_phone', 'users', ['phone_number'], postgresql_where=sa.text('deleted_at IS NULL'))

    # Create service_types table
    op.create_table(
        'service_types',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text()),
        sa.Column('icon_name', sa.String(50)),
        sa.Column('color_hex', sa.String(7)),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Seed service types
    op.execute("""
        INSERT INTO service_types (name, slug, description, icon_name, color_hex, sort_order) VALUES
        ('Food', 'food', 'Soup kitchens, food pantries, meal services', 'utensils', '#FF6B6B', 1),
        ('Shelter', 'shelter', 'Emergency and overnight shelters', 'bed', '#4ECDC4', 2),
        ('Hygiene', 'hygiene', 'Showers, laundry, bathrooms', 'shower', '#45B7D1', 3),
        ('Medical', 'medical', 'Healthcare, mental health, substance abuse', 'heart', '#96CEB4', 4),
        ('Warming Center', 'warming', 'Winter warming centers', 'fire', '#FFEAA7', 5),
        ('Cooling Center', 'cooling', 'Summer cooling centers', 'snowflake', '#74B9FF', 6),
        ('Social Services', 'social', 'Case management, benefits assistance', 'users', '#A29BFE', 7);
    """)

    # Create service_locations table (NO PostGIS - just lat/lon columns)
    op.create_table(
        'service_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('organization_name', sa.String(255)),
        sa.Column('street_address', sa.String(255)),
        sa.Column('city', sa.String(100), default='New York'),
        sa.Column('state', sa.String(2), default='NY'),
        sa.Column('zip_code', sa.String(10)),
        sa.Column('borough', sa.String(50)),
        # Simple lat/lon columns instead of PostGIS geography
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('website', sa.String(500)),
        sa.Column('email', sa.String(255)),
        sa.Column('wheelchair_accessible', sa.Boolean()),
        sa.Column('languages_spoken', postgresql.ARRAY(sa.String())),
        sa.Column('data_source', sa.String(100)),
        sa.Column('external_id', sa.String(255)),
        sa.Column('verified', sa.Boolean(), default=False),
        sa.Column('verification_date', sa.DateTime(timezone=True)),
        sa.Column('city_code', sa.String(10), default='NYC'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # Create indexes
    op.create_index('idx_locations_lat_lon', 'service_locations', ['latitude', 'longitude'])
    op.create_index('idx_locations_city', 'service_locations', ['city_code'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_locations_borough', 'service_locations', ['borough'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_locations_verified', 'service_locations', ['verified'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_locations_external_id', 'service_locations', ['external_id', 'data_source'])

    # Create location_services (many-to-many)
    op.create_table(
        'location_services',
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('service_locations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('service_type_id', sa.Integer(), sa.ForeignKey('service_types.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('capacity', sa.Integer()),
    )
    op.create_index('idx_location_services_service_type', 'location_services', ['service_type_id'])

    # Create operating_hours table
    op.create_table(
        'operating_hours',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('service_locations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('service_type_id', sa.Integer(), sa.ForeignKey('service_types.id', ondelete='CASCADE')),
        sa.Column('day_of_week', sa.Integer(), sa.CheckConstraint('day_of_week >= 0 AND day_of_week <= 6')),
        sa.Column('open_time', sa.Time()),
        sa.Column('close_time', sa.Time()),
        sa.Column('is_24_hours', sa.Boolean(), default=False),
        sa.Column('is_closed', sa.Boolean(), default=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('idx_operating_hours_location', 'operating_hours', ['location_id'])
    op.create_index('idx_operating_hours_day', 'operating_hours', ['day_of_week'])

    # Create temporary_closures table
    op.create_table(
        'temporary_closures',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('service_locations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date()),
        sa.Column('reason', sa.String(255)),
        sa.Column('description', sa.Text()),
        sa.Column('alert_type', sa.String(50), default='closure'),
        sa.Column('is_urgent', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('is_active', sa.Boolean(), default=True),
    )
    op.create_index('idx_closures_location', 'temporary_closures', ['location_id'])
    op.create_index('idx_closures_dates', 'temporary_closures', ['start_date', 'end_date'], postgresql_where=sa.text('is_active = TRUE'))

    # Create user_favorites table
    op.create_table(
        'user_favorites',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('service_locations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_favorites_user', 'user_favorites', ['user_id'])

    # Create analytics_events table
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('session_hash', sa.String(64)),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('service_locations.id', ondelete='SET NULL')),
        sa.Column('service_type_id', sa.Integer(), sa.ForeignKey('service_types.id', ondelete='SET NULL')),
        sa.Column('borough', sa.String(50)),
        sa.Column('event_data', postgresql.JSONB),
    )
    op.create_index('idx_analytics_created_at', 'analytics_events', [sa.text('created_at DESC')])
    op.create_index('idx_analytics_event_type', 'analytics_events', ['event_type'])
    op.create_index('idx_analytics_location', 'analytics_events', ['location_id'], postgresql_where=sa.text('location_id IS NOT NULL'))


def downgrade() -> None:
    op.drop_table('analytics_events')
    op.drop_table('user_favorites')
    op.drop_table('temporary_closures')
    op.drop_table('operating_hours')
    op.drop_table('location_services')
    op.drop_table('service_locations')
    op.drop_table('service_types')
    op.drop_table('users')

    op.execute("DROP EXTENSION IF EXISTS \"uuid-ossp\" CASCADE;")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto CASCADE;")
