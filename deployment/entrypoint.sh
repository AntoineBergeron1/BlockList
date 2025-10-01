#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Django deployment script..."

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

# Create superuser if it doesn't exist (optional)
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('ℹ️ Superuser already exists')
" || true

echo "✅ Django setup complete!"

# Start Django development server
echo "🎯 Starting Django server on 0.0.0.0:8000..."
exec python manage.py runserver 0.0.0.0:8000