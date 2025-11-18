from unittest.mock import Mock, patch

import pytest

from deepweb.models import IPAddress


@pytest.mark.django_db
class TestGeoIPEnrichment:
    """Tests for GeoIP enrichment functionality."""

    def test_enrich_geoip_success(self):
        """Test successful GeoIP enrichment."""
        ip = IPAddress.objects.create(address="8.8.8.8")
        result = ip.enrich_geoip()

        assert result is True
        assert ip.country_code is not None or ip.asn is not None

    def test_enrich_geoip_private_ip(self):
        """Test GeoIP enrichment with private IP (should not crash)."""
        ip = IPAddress.objects.create(address="192.168.1.1")
        result = ip.enrich_geoip()

        # Should return True but no data
        assert result is True
        assert ip.country_code is None
        assert ip.asn is None

    def test_enrich_geoip_ipv6(self):
        """Test GeoIP enrichment with IPv6 address."""
        ip = IPAddress.objects.create(address="2001:4860:4860::8888")
        result = ip.enrich_geoip()

        assert result is True
        # Google DNS should have country and ASN
        assert ip.country_code is not None
        assert ip.asn is not None

    def test_enrich_geoip_no_duplication(self):
        """Test that re-enrichment doesn't duplicate data."""
        ip = IPAddress.objects.create(address="8.8.8.8")
        ip.enrich_geoip()

        country_before = ip.country_name
        asn_before = ip.asn

        # Re-enrich
        ip.enrich_geoip()

        assert ip.country_name == country_before
        assert ip.asn == asn_before

    @patch("django.contrib.gis.geoip2.GeoIP2")
    def test_enrich_geoip_database_missing(self, mock_geoip):
        """Test GeoIP enrichment when database is missing."""
        mock_geoip.side_effect = Exception("Database not found")

        ip = IPAddress.objects.create(address="8.8.8.8")
        result = ip.enrich_geoip()

        # Should return False on error
        assert result is False

    def test_enrich_geoip_updates_only_geo_fields(self):
        """Test that enrich_geoip only updates geo fields."""
        ip = IPAddress.objects.create(address="8.8.8.8")
        ip.hostname = "dns.google"
        ip.reputation_score = 50
        ip.save()

        ip.enrich_geoip()

        # Refresh from DB
        ip.refresh_from_db()

        # Geo fields should be updated
        assert ip.country_code is not None or ip.asn is not None

        # Other fields should remain unchanged
        assert ip.hostname == "dns.google"
        assert ip.reputation_score == 50
