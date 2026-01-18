#!/bin/bash

# Hope Platform - Direct PostgreSQL Setup (No Docker)
# For Oracle Linux 9

set -e

echo "================================================"
echo "Hope Platform - Direct Setup (No Docker)"
echo "================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./setup-direct.sh"
    exit 1
fi

# Install PostgreSQL 15 with PostGIS
echo ""
echo "📦 Installing PostgreSQL 15 with PostGIS..."
dnf install -y postgresql15-server postgresql15-contrib postgis34_15

# Initialize PostgreSQL
echo ""
echo "🔧 Initializing PostgreSQL..."
/usr/pgsql-15/bin/postgresql-15-setup initdb

# Start and enable PostgreSQL
echo ""
echo "🚀 Starting PostgreSQL..."
systemctl start postgresql-15
systemctl enable postgresql-15

# Wait for PostgreSQL to start
sleep 5

# Create database and user
echo ""
echo "🗄️  Creating database and user..."
sudo -u postgres psql -c "CREATE USER hope_user WITH PASSWORD 'hope_password';"
sudo -u postgres psql -c "CREATE DATABASE hope_db OWNER hope_user;"
sudo -u postgres psql -d hope_db -c "CREATE EXTENSION postgis;"
sudo -u postgres psql -d hope_db -c "CREATE EXTENSION \"uuid-ossp\";"
sudo -u postgres psql -d hope_db -c "CREATE EXTENSION pgcrypto;"

# Configure PostgreSQL to allow local connections
echo ""
echo "🔐 Configuring PostgreSQL authentication..."
cat >> /var/lib/pgsql/15/data/pg_hba.conf << EOF

# Hope Platform
local   hope_db         hope_user                               md5
host    hope_db         hope_user       127.0.0.1/32            md5
host    hope_db         hope_user       ::1/128                 md5
EOF

# Restart PostgreSQL
systemctl restart postgresql-15

# Create backend .env
echo ""
echo "📝 Creating environment files..."
cd /home/opc/Hope

cat > backend/.env << 'EOF'
DATABASE_URL=postgresql+asyncpg://hope_user:hope_password@localhost:5432/hope_db
SECRET_KEY=dev-secret-key-change-in-production
ENCRYPTION_KEY=dev-encryption-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
ALLOWED_ORIGINS=http://localhost:8081,exp://localhost:19000
ENVIRONMENT=development
RATE_LIMIT_ENABLED=true
REDIS_URL=redis://localhost:6379/0
EOF

cat > scraper/.env << 'EOF'
DATABASE_URL=postgresql://hope_user:hope_password@localhost:5432/hope_db
NYC_OPEN_DATA_APP_TOKEN=
USER_AGENT=HopePlatform/1.0 (NYC Homeless Services)
EOF

# Set ownership
chown opc:opc backend/.env scraper/.env

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "PostgreSQL is running and database is ready."
echo ""
echo "Next steps:"
echo ""
echo "1. Install Python dependencies and run migrations:"
echo "   cd /home/opc/Hope/backend"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   alembic upgrade head"
echo ""
echo "2. Start the backend:"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "3. In another terminal, run the scraper:"
echo "   cd /home/opc/Hope/scraper"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   python -m scraper.main"
echo ""
