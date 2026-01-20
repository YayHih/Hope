# Hope for NYC

A free, privacy-focused directory of essential services for homeless individuals in New York City.

**[hopefornyc.com](https://hopefornyc.com)**

No ads. No tracking. Just help when you need it.

---

## What It Does

Hope for NYC helps people find:
- Emergency shelters & intake centers
- Food pantries & soup kitchens
- Hygiene facilities
- Medical services
- Mental health resources
- Legal aid
- Free WiFi & charging (LinkNYC)
- Public restrooms

**Features:**
- Real-time "Open Now" and "Open Today" filters
- Dark mode support (follows system preference)
- English & Spanish
- Mobile-first design
- No account required

---

## Tech Stack

**Frontend**
- React 18 + TypeScript
- Leaflet maps with marker clustering
- i18n (English/Spanish)
- Dark/light theme support

**Backend**
- FastAPI (Python) with 4 uvicorn workers
- PostgreSQL 15 with spatial indexes
- Redis for rate limiting
- SQLAlchemy async ORM

**Infrastructure**
- Oracle Linux 9 (ARM64)
- Nginx with SSL (Let's Encrypt)
- Systemd services

---

## Quick Start

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your database credentials

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install

cp .env.example .env
# Edit .env with your API URL

npm start
```

### Production Build

```bash
cd frontend
npm run build
sudo rsync -av --delete build/ /var/www/hope-frontend/
```

---

## Project Structure

```
Hope/
├── backend/
│   ├── app/
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── models/       # SQLAlchemy models
│   │   └── schemas/      # Pydantic schemas
│   ├── alembic/          # Database migrations
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── screens/      # MapScreen, AboutScreen, etc.
│   │   ├── components/   # Header, BottomNav
│   │   ├── i18n/         # Translations
│   │   └── theme/        # Theming system
│   └── public/
│
└── scraper/              # Data collection scripts
```

---

## API

### Public Endpoints

**GET /api/v1/public/service-types**
Returns available service categories.

**GET /api/v1/public/services/in-bounds**
Returns services within a map viewport.

Query params:
- `min_lat`, `max_lat`, `min_lng`, `max_lng` (required)
- `center_lat`, `center_lng` (for distance sorting)
- `service_types[]` (filter by category)
- `open_now=true` (filter by currently open)
- `open_today=true` (filter by open any time today)
- `limit` (default 75)

**GET /api/v1/public/services/{id}**
Returns details for a specific location.

**POST /api/v1/public/issues/report**
Submit a correction or report.

---

## Environment Variables

### Backend (.env)

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/hope_db
SECRET_KEY=your-secret-key
REDIS_URL=redis://localhost:6379
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Frontend (.env)

```bash
REACT_APP_API_BASE_URL=https://yourdomain.com/api/v1
REACT_APP_RECAPTCHA_SITE_KEY=your-recaptcha-site-key
```

---

## Privacy

- No user accounts
- No tracking or analytics
- No cookies (except admin session)
- No data collection
- HTTPS enforced

---

## Data Sources

- NYC Open Data Portal
- Department of Homeless Services
- Community organizations
- Manual verification

---

## License

### Code

Licensed under **[AGPL-3.0](LICENSE)**.

You can use, modify, and distribute this code. If you run a modified version as a web service, you must share your source code under the same license.

### Brand

The name "Hope for NYC", logos, and domain hopefornyc.com are trademarks.

You **can**:
- Fork this to create "Hope for [Your City]"
- Use the codebase for your own directory
- Credit this project as the original

You **cannot**:
- Use the "Hope for NYC" name for a competing site
- Imply official endorsement

---

## Contact

**Issues or corrections:** campuslens.help@gmail.com
**Emergency shelter:** Call 311 (NYC)

---

Built for New York City.
