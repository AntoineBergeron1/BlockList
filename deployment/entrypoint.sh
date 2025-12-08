#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Django deployment script..."

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    echo "✅ Node.js installed: $(node --version)"
fi

# Wait for database to be ready
echo "⏳ Waiting for PostgreSQL..."
sleep 10
echo "✅ PostgreSQL should be ready!"

# Navigate to Django app directory
cd /app/src

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install --production

# Download GeoIP databases if not present
echo "🌍 Checking GeoIP databases..."
if [ ! -f /app/src/geoip_data/GeoLite2-City.mmdb ] || [ ! -f /app/src/geoip_data/GeoLite2-ASN.mmdb ]; then
    if [ -n "$MAXMIND_LICENSE_KEY" ]; then
        echo "📥 Downloading MaxMind GeoIP databases..."
        cd /app/src/geoip_data
        bash download_geoip.sh "$MAXMIND_LICENSE_KEY"
        cd /app/src
        echo "✅ GeoIP databases downloaded"
    else
        echo "⚠️  WARNING: MAXMIND_LICENSE_KEY not set, GeoIP enrichment will not work"
    fi
else
    echo "✅ GeoIP databases already present"
fi

# Clean up any stale migration issues
echo "🧹 Cleaning up migrations if needed..."
python manage.py migrate --fake-initial 2>/dev/null || true

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || true

# Generate version file if it doesn't exist (for local dev)
echo "🔖 Checking version info..."
if [ ! -f /app/src/version.txt ]; then
    echo "Generating version.txt..."
    cd /app
    git rev-parse --short HEAD > /app/src/version.txt 2>/dev/null || echo "dev" > /app/src/version.txt
    cd /app/src
else
    echo "version.txt already exists (from deploy workflow)"
fi

# Create test users (for development quick login)
echo "👤 Creating test users..."
python manage.py create_test_users || true

# Set up cron job for daily reputation recalculation
echo "Setting up cron job for reputation recalculation..."
apt-get update -qq && apt-get install -y -qq cron > /dev/null 2>&1
echo "0 3 * * * cd /app/src && /usr/local/bin/python manage.py recalculate_reputation >> /var/log/reputation_cron.log 2>&1" | crontab -
service cron start
echo "Cron job configured (runs daily at 3 AM)"

echo "✅ Django setup complete!"

# Start Django development server
echo "🎯 Starting Django server on 0.0.0.0:8000..."
exec python manage.py runserver 0.0.0.0:8000
