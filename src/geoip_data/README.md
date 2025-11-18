# MaxMind GeoIP2 Databases

This directory contains MaxMind GeoLite2 databases for IP geolocation.

## Required Databases

- `GeoLite2-City.mmdb` - City, country, coordinates
- `GeoLite2-ASN.mmdb` - ASN, ISP/organization

## Download Instructions

### Option 1: Using the script (Recommended)

```bash
cd src/geoip_data
./download_geoip.sh YOUR_MAXMIND_LICENSE_KEY
```

Or set environment variable:
```bash
export MAXMIND_LICENSE_KEY="your_key_here"
./download_geoip.sh
```

### Option 2: Manual download

1. Login to https://www.maxmind.com/en/account/login
2. Navigate to "Download Files" in GeoIP menu
3. Download:
   - GeoLite2 City (MMDB format)
   - GeoLite2 ASN (MMDB format)
4. Extract `.mmdb` files to this directory

## License Key

To get a free MaxMind license key:
1. Sign up at https://www.maxmind.com/en/geolite2/signup
2. Generate a license key in your account
3. Free tier allows 30 downloads per day

## Update Frequency

**Important**: GeoLite2 End User License Agreement requires:
- Databases must be updated every 30 days maximum
- Old databases must be deleted after new release

Consider setting up a cron job for automatic updates.

## Production Deployment

For production, add the license key to `.env`:
```
MAXMIND_LICENSE_KEY=your_key_here
```

Then run the download script during deployment.
