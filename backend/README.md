# Hope Backend

FastAPI-based backend for the Hope Platform - NYC homeless services directory.

## Tech Stack

- **FastAPI** - Async Python web framework
- **SQLAlchemy** 2.x - Async ORM with PostgreSQL
- **PostgreSQL** - Primary database with uuid-ossp and pgcrypto extensions
- **Redis** - Rate limit storage (shared across workers)
- **Uvicorn** - ASGI server
- **Alembic** - Database migrations
- **slowapi** - Rate limiting

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (see .env.example)
cp .env.example .env

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│     users       │       │ service_locations│       │  service_types  │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ id (UUID) PK    │       │ id (UUID) PK     │       │ id (INT) PK     │
│ phone_number    │       │ name             │       │ name            │
│ phone_verified  │       │ latitude         │       │ slug (unique)   │
│ preferences     │       │ longitude        │       │ description     │
│ created_at      │       │ street_address   │       │ icon_name       │
│ last_login_at   │       │ borough          │       │ color_hex       │
│ deleted_at      │       │ phone            │       │ sort_order      │
└────────┬────────┘       │ ...              │       │ active          │
         │                └────────┬─────────┘       └────────┬────────┘
         │                         │                          │
         │                         │                          │
         ▼                         ▼                          ▼
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│ user_favorites  │       │location_services │       │ operating_hours │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ user_id (FK) PK │◄──────│ location_id (FK) │───────│ location_id(FK) │
│ location_id(FK) │       │ service_type_id  │       │ service_type_id │
│ created_at      │       │ notes            │       │ day_of_week     │
└─────────────────┘       │ capacity         │       │ open_time       │
                          └──────────────────┘       │ close_time      │
                                                     │ is_24_hours     │
┌─────────────────┐       ┌──────────────────┐       │ is_closed       │
│ analytics_events│       │temporary_closures│       └─────────────────┘
├─────────────────┤       ├──────────────────┤
│ id (BIGINT) PK  │       │ id (UUID) PK     │
│ event_type      │       │ location_id (FK) │
│ session_hash    │       │ start_date       │
│ location_id(FK) │       │ end_date         │
│ service_type_id │       │ reason           │
│ borough         │       │ alert_type       │
│ event_data      │       │ is_urgent        │
└─────────────────┘       │ created_by (FK)  │
                          └──────────────────┘
```

### Tables

#### `users`
Minimal PII user accounts for optional authentication features.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, default uuid4 | Primary key |
| `phone_number` | VARCHAR(20) | UNIQUE | Phone for OTP auth (encrypted) |
| `phone_verified` | BOOLEAN | default FALSE | Phone verification status |
| `preferences` | JSONB | default {} | User preferences |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |
| `last_login_at` | TIMESTAMPTZ | | Last login time |
| `deleted_at` | TIMESTAMPTZ | | Soft delete (GDPR) |

#### `service_locations`
Physical locations offering services.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, default uuid4 | Primary key |
| `name` | VARCHAR(255) | NOT NULL | Location name |
| `description` | TEXT | | Description |
| `organization_name` | VARCHAR(255) | | Parent organization |
| `street_address` | VARCHAR(255) | | Street address |
| `city` | VARCHAR(100) | default "New York" | City |
| `state` | VARCHAR(2) | default "NY" | State code |
| `zip_code` | VARCHAR(10) | | ZIP code |
| `borough` | VARCHAR(50) | | NYC borough |
| `latitude` | FLOAT | | Latitude coordinate |
| `longitude` | FLOAT | | Longitude coordinate |
| `phone` | VARCHAR(20) | | Contact phone |
| `website` | VARCHAR(500) | | Website URL |
| `email` | VARCHAR(255) | | Contact email |
| `wheelchair_accessible` | BOOLEAN | | Accessibility flag |
| `languages_spoken` | TEXT[] | | Array of languages |
| `data_source` | VARCHAR(100) | | Data origin (e.g., "NYC Open Data") |
| `external_id` | VARCHAR(255) | | External system ID |
| `verified` | BOOLEAN | default FALSE | Verification status |
| `verification_date` | TIMESTAMPTZ | | Last verification |
| `city_code` | VARCHAR(10) | default "NYC" | Multi-city support |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default now() | Update timestamp |
| `deleted_at` | TIMESTAMPTZ | | Soft delete |

#### `service_types`
Service categorization (Food, Shelter, Hygiene, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO | Primary key |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | Display name |
| `slug` | VARCHAR(100) | NOT NULL, UNIQUE | URL-safe identifier |
| `description` | TEXT | | Description |
| `icon_name` | VARCHAR(50) | | Icon identifier |
| `color_hex` | VARCHAR(7) | | Marker color (e.g., "#FF6B6B") |
| `sort_order` | INTEGER | default 0 | Display order |
| `active` | BOOLEAN | default TRUE | Active status |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |

**Current Service Types:**
| ID | Name | Slug | Color |
|----|------|------|-------|
| 1 | Food | food | #FF6B6B |
| 11 | Intake Center | intake | #E53E3E |
| 12 | Drop-In Center | drop-in | #DD6B20 |
| 15 | Mental Health Crisis | mental-health-crisis | #E91E63 |
| 17 | Youth Services | youth-services | #38B2AC |
| 13 | Free WiFi & Charging | free-wifi-linknyc | #4299E1 |
| 16 | Benefits & ID Help | benefits-id | #9F7AEA |
| 7 | Case Management | social | #A29BFE |
| 3 | Hygiene | hygiene | #45B7D1 |
| 4 | Medical | medical | #96CEB4 |
| 8 | Hospitals | hospitals | #E74C3C |
| 14 | Public Restrooms | public-restrooms | #8B5CF6 |
| 5 | Warming Center | warming | #FF8C00 |
| 6 | Cooling Center | cooling | #74B9FF |
| 18 | DV Hotline | dv-hotline | #9C27B0 |

#### `location_services`
Many-to-many relationship between locations and service types.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `location_id` | UUID | PK, FK → service_locations.id, ON DELETE CASCADE | Location reference |
| `service_type_id` | INTEGER | PK, FK → service_types.id, ON DELETE CASCADE | Service type reference |
| `notes` | TEXT | | Service-specific notes (e.g., "ID required") |
| `capacity` | INTEGER | | Capacity (beds, meals, etc.) |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |

#### `operating_hours`
Operating hours for locations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, AUTO | Primary key |
| `location_id` | UUID | NOT NULL, FK → service_locations.id, ON DELETE CASCADE | Location reference |
| `service_type_id` | INTEGER | FK → service_types.id, ON DELETE CASCADE | Optional service-specific hours |
| `day_of_week` | INTEGER | NOT NULL, CHECK (0-6) | 0=Sunday, 6=Saturday |
| `open_time` | TIME | | Opening time (24h format) |
| `close_time` | TIME | | Closing time (24h format) |
| `is_24_hours` | BOOLEAN | default FALSE | Open 24 hours flag |
| `is_closed` | BOOLEAN | default FALSE | Closed this day flag |
| `notes` | TEXT | | Notes (e.g., "Last entry 30min before closing") |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, default now() | Update timestamp |

#### `temporary_closures`
Temporary closures and alerts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, default uuid4 | Primary key |
| `location_id` | UUID | NOT NULL, FK → service_locations.id, ON DELETE CASCADE | Location reference |
| `start_date` | DATE | NOT NULL | Closure start date |
| `end_date` | DATE | | End date (NULL = indefinite) |
| `reason` | VARCHAR(255) | | Reason (Holiday, Maintenance, etc.) |
| `description` | TEXT | | Detailed description |
| `alert_type` | VARCHAR(50) | default "closure" | Type: closure, schedule_change, capacity_limit |
| `is_urgent` | BOOLEAN | default FALSE | Priority flag |
| `is_active` | BOOLEAN | default TRUE | Active status |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |
| `created_by` | UUID | FK → users.id | Admin who created |

#### `user_favorites`
User's saved locations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | UUID | PK, FK → users.id, ON DELETE CASCADE | User reference |
| `location_id` | UUID | PK, FK → service_locations.id, ON DELETE CASCADE | Location reference |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |

#### `analytics_events`
Anonymous analytics (no PII).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGINT | PK, AUTO | Primary key |
| `event_type` | VARCHAR(50) | NOT NULL | Event type (map_view, location_click, etc.) |
| `session_hash` | VARCHAR(64) | | Ephemeral session ID (24h TTL) |
| `location_id` | UUID | FK → service_locations.id, ON DELETE SET NULL | Location reference |
| `service_type_id` | INTEGER | FK → service_types.id, ON DELETE SET NULL | Service type reference |
| `borough` | VARCHAR(50) | | Geographic aggregation (borough only, not GPS) |
| `event_data` | JSONB | | Additional event data |
| `created_at` | TIMESTAMPTZ | NOT NULL, default now() | Creation timestamp |

### PostgreSQL Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;      -- Encryption for PII
```

## API Routes

Base URL: `/api/v1/public`

### GET `/service-types`
Get all service types for filter UI.

**Rate Limit:** 100/minute

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `active_only` | bool | true | Only return active service types |

**Response:** `List[ServiceTypeResponse]`
```json
[
  {
    "id": 1,
    "name": "Food",
    "slug": "food",
    "description": "Soup kitchens, food pantries, meal services",
    "icon_name": "utensils",
    "color_hex": "#FF6B6B"
  }
]
```

### GET `/services/nearby`
Find services near a location.

**Rate Limit:** 60/minute

**Query Parameters:**
| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `latitude` | float | Yes | - | -90 to 90 | User's latitude |
| `longitude` | float | Yes | - | -180 to 180 | User's longitude |
| `radius_km` | float | No | 5.0 | 0.1 to 50 | Search radius in km |
| `service_types` | List[str] | No | - | - | Filter by service type slugs |
| `open_now` | bool | No | false | - | Only open locations |
| `limit` | int | No | 50 | 1 to 500 | Max results |

**Response:** `List[ServiceLocationResponse]`

### GET `/services/in-bounds`
Find services within a bounding box (viewport query).

**Rate Limit:** 60/minute

**Query Parameters:**
| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `min_lat` | float | Yes | - | -90 to 90 | South bound |
| `max_lat` | float | Yes | - | -90 to 90 | North bound |
| `min_lng` | float | Yes | - | -180 to 180 | West bound |
| `max_lng` | float | Yes | - | -180 to 180 | East bound |
| `center_lat` | float | No | - | -90 to 90 | Center for distance sorting |
| `center_lng` | float | No | - | -180 to 180 | Center for distance sorting |
| `service_types` | List[str] | No | - | - | Filter by service type slugs |
| `exclude_service_types` | List[str] | No | - | - | Exclude service type slugs |
| `open_now` | bool | No | false | - | Only currently open |
| `open_today` | bool | No | false | - | Open any time today |
| `limit` | int | No | 75 | 1 to 100 | Max results |

**Validation:**
- `min_lat` must be less than `max_lat`
- `min_lng` must be less than `max_lng`

**Response:** `List[ServiceLocationResponse]`
```json
[
  {
    "id": "uuid",
    "name": "Holy Apostles Soup Kitchen",
    "description": null,
    "latitude": 40.7425,
    "longitude": -74.0005,
    "distance_km": 0.5,
    "street_address": "296 9th Ave",
    "borough": "Manhattan",
    "phone": "(212) 555-1234",
    "services": [
      {
        "type": "food",
        "name": "Food",
        "notes": "Hot meals served",
        "capacity": 1000
      }
    ],
    "operating_hours": [
      {
        "day_of_week": 1,
        "day_name": "Monday",
        "open_time": "10:00:00",
        "close_time": "14:00:00",
        "is_24_hours": false,
        "is_closed": false,
        "notes": null
      }
    ],
    "is_open_now": true,
    "next_open_time": null
  }
]
```

### GET `/services/{location_id}`
Get detailed information for a specific location.

**Rate Limit:** 100/minute

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `location_id` | UUID | Location ID |

**Response:** `ServiceLocationDetail`
```json
{
  "id": "uuid",
  "name": "Holy Apostles Soup Kitchen",
  "description": "Largest emergency food program in NYC",
  "organization_name": "Church of the Holy Apostles",
  "latitude": 40.7425,
  "longitude": -74.0005,
  "street_address": "296 9th Ave",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "borough": "Manhattan",
  "phone": "(212) 555-1234",
  "website": "https://example.com",
  "email": "info@example.com",
  "wheelchair_accessible": true,
  "languages_spoken": ["English", "Spanish"],
  "services": [...],
  "operating_hours": [...],
  "current_closures": [],
  "verified": true,
  "last_updated": "2024-01-15T12:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Service location not found"
}
```

### POST `/issues/report`
Submit an issue report about a location.

**Rate Limit:** 10/hour

**Request Body:**
```json
{
  "issue_type": "hours",
  "location_name": "Holy Apostles Soup Kitchen",
  "description": "The hours listed are incorrect. They close at 1pm not 2pm.",
  "captcha_token": "recaptcha-token"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `issue_type` | string | Yes | Enum: closed, hours, full, referral, other | Issue category |
| `location_name` | string | Yes | 1-200 chars | Location name |
| `description` | string | Yes | 1-1000 chars | Issue details |
| `captcha_token` | string | Yes | - | reCAPTCHA v2 token |

**Response:**
```json
{
  "status": "success",
  "message": "Thank you for your report. We will review it shortly."
}
```

**Error Responses:**
- `400`: reCAPTCHA verification failed
- `500`: Email sending failed

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "environment": "production",
  "version": "1.0.0"
}
```

## Rate Limiting

Rate limits are enforced per IP address using Redis for shared storage across workers.

| Endpoint | Limit |
|----------|-------|
| `/service-types` | 100/minute |
| `/services/nearby` | 60/minute |
| `/services/in-bounds` | 60/minute |
| `/services/{id}` | 100/minute |
| `/issues/report` | 10/hour |

## Database Connection Pool

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,        # Active connections
    max_overflow=10,     # Extra connections during spikes
    pool_timeout=30,     # Wait time for connection
    pool_pre_ping=True,  # Verify connections
)
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost/hope` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `ENVIRONMENT` | Runtime environment | `development` or `production` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["https://hopefornyc.com"]` |
| `RECAPTCHA_SECRET_KEY` | Google reCAPTCHA secret | `6Le...` |

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Settings and configuration
│   ├── database.py          # SQLAlchemy async engine
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── user_favorite.py
│   │   ├── service_location.py
│   │   ├── location_service.py
│   │   ├── service_type.py
│   │   ├── operating_hours.py
│   │   ├── temporary_closure.py
│   │   └── analytics_event.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── public.py        # Public API endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── service.py       # Pydantic models for services
│   │   └── report.py        # Pydantic models for reports
│   └── services/
│       ├── __init__.py
│       ├── geospatial_service.py  # Location queries
│       └── email_service.py       # Email notifications
├── alembic/
│   ├── env.py
│   └── versions/            # Migration files
├── requirements.txt
├── .env.example
└── README.md
```

## Production Deployment

The backend runs behind Nginx reverse proxy:

```bash
# Start with systemd (recommended)
sudo systemctl start hope-backend

# Or manual start
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
```

**Nginx Configuration:**
- Proxies `/api/` to uvicorn backend
- Sets `X-Forwarded-For` header for rate limiting
- Rate limiting uses Redis storage shared across all workers

## Security

- **Rate Limiting**: Redis-backed, shared across workers
- **CORS**: Configurable allowed origins
- **reCAPTCHA**: Protects form submissions
- **Input Sanitization**: Pydantic validation, HTML stripping
- **Soft Deletes**: GDPR compliance for user data
- **No PII in Analytics**: Only borough-level geographic data

## License

GNU AGPL v3 - See LICENSE file for details.
