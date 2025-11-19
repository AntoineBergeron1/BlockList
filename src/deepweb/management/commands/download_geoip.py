"""
Django management command to download MaxMind GeoIP2 databases.
Usage: python manage.py download_geoip
"""

import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Download MaxMind GeoIP2 databases (GeoLite2-City and GeoLite2-ASN)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--license-key",
            type=str,
            help="MaxMind license key (or set MAXMIND_LICENSE_KEY env var)",
        )

    def handle(self, *args, **options):
        license_key = options.get("license_key") or os.getenv("MAXMIND_LICENSE_KEY")

        if not license_key:
            raise CommandError(
                "MaxMind license key required. "
                "Use --license-key or set MAXMIND_LICENSE_KEY environment variable."
            )

        geoip_path = settings.GEOIP_PATH
        script_path = geoip_path / "download_geoip.sh"

        if not script_path.exists():
            raise CommandError(f"Download script not found: {script_path}")

        self.stdout.write("Downloading MaxMind GeoIP2 databases...")

        try:
            result = subprocess.run(
                [str(script_path), license_key],
                cwd=str(geoip_path),
                check=True,
                capture_output=True,
                text=True,
            )

            self.stdout.write(result.stdout)
            self.stdout.write(
                self.style.SUCCESS("✅ GeoIP databases downloaded successfully!")
            )

            # Verify files exist
            city_db = geoip_path / "GeoLite2-City.mmdb"
            asn_db = geoip_path / "GeoLite2-ASN.mmdb"

            if city_db.exists() and asn_db.exists():
                city_size = city_db.stat().st_size / (1024 * 1024)
                asn_size = asn_db.stat().st_size / (1024 * 1024)
                self.stdout.write(f"  - GeoLite2-City.mmdb: {city_size:.1f} MB")
                self.stdout.write(f"  - GeoLite2-ASN.mmdb: {asn_size:.1f} MB")
            else:
                raise CommandError("Download completed but database files not found")

        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(e.stdout))
            self.stdout.write(self.style.ERROR(e.stderr))
            raise CommandError(f"Failed to download GeoIP databases: {e}")
