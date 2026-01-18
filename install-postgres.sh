#!/bin/bash

# Install PostgreSQL on Oracle Linux 9

set -e

echo "================================================"
echo "Installing PostgreSQL 15"
echo "================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./install-postgres.sh"
    exit 1
fi

# Enable PostgreSQL 15 module
echo "📦 Enabling PostgreSQL 15 module..."
dnf module enable -y postgresql:15

# Install PostgreSQL
echo "📦 Installing PostgreSQL server and contrib..."
dnf install -y postgresql-server postgresql-contrib

# Initialize database
echo "🔧 Initializing PostgreSQL..."
postgresql-setup --initdb

# Start PostgreSQL
echo "🚀 Starting PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Wait for startup
sleep 5

# Create database and user
echo "🗄️  Creating hope_db database..."
sudo -u postgres psql << 'EOF'
CREATE USER hope_user WITH PASSWORD 'hope_password';
CREATE DATABASE hope_db OWNER hope_user;
\c hope_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
EOF

# Configure authentication
echo "🔐 Configuring authentication..."
echo "local   hope_db         hope_user                               md5" >> /var/lib/pgsql/data/pg_hba.conf
echo "host    hope_db         hope_user       127.0.0.1/32            md5" >> /var/lib/pgsql/data/pg_hba.conf

# Restart PostgreSQL
systemctl restart postgresql

# Create .env files
echo "📝 Creating environment files..."
cat > /home/opc/Hope/backend/.env << 'ENVEOF'
DATABASE_URL=postgresql+asyncpg://hope_user:hope_password@localhost:5432/hope_db
SECRET_KEY=dev-secret-key-change-in-production
ENCRYPTION_KEY=dev-encryption-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
ALLOWED_ORIGINS=http://localhost:8081,exp://localhost:19000
ENVIRONMENT=development
RATE_LIMIT_ENABLED=true
REDIS_URL=redis://localhost:6379/0
ENVEOF

cat > /home/opc/Hope/scraper/.env << 'ENVEOF'
DATABASE_URL=postgresql://hope_user:hope_password@localhost:5432/hope_db
NYC_OPEN_DATA_APP_TOKEN=
USER_AGENT=HopePlatform/1.0
ENVEOF

chown opc:opc /home/opc/Hope/backend/.env /home/opc/Hope/scraper/.env

echo ""
echo "✅ PostgreSQL installed and configured!"
echo ""
echo "Database: hope_db"
echo "User: hope_user"
echo "Password: hope_password"
echo ""
