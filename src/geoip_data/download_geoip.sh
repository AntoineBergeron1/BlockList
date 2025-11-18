#!/bin/bash
# Script to download MaxMind GeoLite2 databases
# Usage: ./download_geoip.sh YOUR_LICENSE_KEY

set -e

LICENSE_KEY="${1:-${MAXMIND_LICENSE_KEY}}"

if [ -z "$LICENSE_KEY" ]; then
    echo "Error: MaxMind license key required"
    echo "Usage: ./download_geoip.sh YOUR_LICENSE_KEY"
    echo "   or: Set MAXMIND_LICENSE_KEY environment variable"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Downloading MaxMind GeoLite2 databases..."

# Download GeoLite2-City
echo "→ Downloading GeoLite2-City..."
curl -o GeoLite2-City.tar.gz \
    "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${LICENSE_KEY}&suffix=tar.gz"

# Download GeoLite2-ASN
echo "→ Downloading GeoLite2-ASN..."
curl -o GeoLite2-ASN.tar.gz \
    "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN&license_key=${LICENSE_KEY}&suffix=tar.gz"

# Extract .mmdb files
echo "→ Extracting databases..."
tar -xzf GeoLite2-City.tar.gz --strip-components=1 --wildcards '*.mmdb'
tar -xzf GeoLite2-ASN.tar.gz --strip-components=1 --wildcards '*.mmdb'

# Cleanup
echo "→ Cleaning up archives..."
rm -f GeoLite2-*.tar.gz

echo "✓ Done! Databases downloaded:"
ls -lh *.mmdb

echo ""
echo "Note: GeoLite2 databases must be updated every 30 days per MaxMind license."
echo "Consider setting up a cron job to automate this."
