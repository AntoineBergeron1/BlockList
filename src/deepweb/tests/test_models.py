"""
Unit tests for deepweb models.
"""

from django.core.exceptions import ValidationError

import pytest

from deepweb.models import IPAddress, Report


@pytest.mark.django_db
@pytest.mark.unit
class TestIPAddressModel:
    """Tests for IPAddress model."""

    def test_create_ipv4_address(self, ip_address_factory):
        """Test creating a valid IPv4 address."""
        ip = ip_address_factory(address="192.168.1.1")
        assert ip.address == "192.168.1.1"
        assert ip.version == IPAddress.IPV4
        assert ip.reputation_score == 100

    def test_create_ipv6_address(self):
        """Test creating a valid IPv6 address."""
        ip = IPAddress.objects.create(address="2001:db8::1")
        assert ip.address == "2001:db8::1"
        assert ip.version == IPAddress.IPV6

    def test_invalid_ip_address(self):
        """Test that invalid IP addresses raise ValidationError."""
        with pytest.raises(ValidationError):
            ip = IPAddress(address="invalid-ip")
            ip.save()

    def test_reputation_calculation_no_reports(self, ip_address_factory):
        """Test reputation score with no reports."""
        ip = ip_address_factory()
        ip.calculate_reputation()
        assert ip.reputation_score == 100

    def test_reputation_calculation_with_reports(
        self, ip_address_factory, report_factory
    ):
        """Test reputation decreases with reports."""
        ip = ip_address_factory()

        # Create 3 reports for this IP
        report_factory.create_batch(3, ip_address=ip)

        ip.calculate_reputation()
        # 100 - (3 * 5) = 85
        assert ip.reputation_score == 85

    def test_string_representation(self, ip_address_factory):
        """Test __str__ method."""
        ip = ip_address_factory(address="8.8.8.8")
        assert str(ip) == "8.8.8.8"


@pytest.mark.django_db
@pytest.mark.unit
class TestReportModel:
    """Tests for Report model."""

    def test_create_report(self, report_factory):
        """Test creating a report."""
        report = report_factory(reason=Report.HACKING)
        assert report.reason == Report.HACKING
        assert report.ip_address is not None
        assert report.user is not None

    def test_report_updates_reputation(self, ip_address_factory, user_factory):
        """Test that creating a report updates IP reputation."""
        ip = ip_address_factory()
        user = user_factory()

        initial_score = ip.reputation_score

        # Create a report
        Report.objects.create(
            ip_address=ip, user=user, reason=Report.SPAM, comment="Test spam report"
        )

        # Refresh IP from database
        ip.refresh_from_db()

        # Score should have decreased
        assert ip.reputation_score < initial_score

    def test_string_representation(self, report_factory):
        """Test __str__ method."""
        report = report_factory(reason=Report.PHISHING)
        assert report.user.username in str(report)
        assert report.ip_address.address in str(report)

    def test_reputation_reaches_minimum(self, ip_address_factory, report_factory):
        """Test reputation cannot go below 0."""
        ip = ip_address_factory()
        report_factory.create_batch(25, ip_address=ip)
        ip.calculate_reputation()
        assert ip.reputation_score == 0

    def test_multiple_reports_same_user(self, ip_address_factory, user_factory):
        """Test multiple reports from same user."""
        ip = ip_address_factory()
        user = user_factory()
        Report.objects.create(ip_address=ip, user=user, reason=Report.SPAM)
        Report.objects.create(ip_address=ip, user=user, reason=Report.HACKING)
        ip.refresh_from_db()
        assert ip.reputation_score == 90

    def test_delete_report_increases_reputation(self, ip_address_factory, user_factory):
        """Test that deleting a report increases IP reputation."""
        ip = ip_address_factory()
        user = user_factory()

        # Create 2 reports
        report1 = Report.objects.create(ip_address=ip, user=user, reason=Report.SPAM)
        Report.objects.create(ip_address=ip, user=user, reason=Report.HACKING)

        ip.refresh_from_db()
        score_with_2_reports = ip.reputation_score

        # Delete one report
        report1.delete()

        ip.refresh_from_db()
        # Score should have increased
        assert ip.reputation_score > score_with_2_reports

    def test_reputation_decay_ignores_old_reports(
        self, ip_address_factory, user_factory
    ):
        """Test that reports older than max_age_days are ignored."""
        from datetime import timedelta

        from django.utils import timezone

        ip = ip_address_factory()
        user = user_factory()

        # Create a report
        report = Report.objects.create(ip_address=ip, user=user, reason=Report.SPAM)

        # Manually set the report date to 35 days ago
        old_date = timezone.now() - timedelta(days=35)
        Report.objects.filter(pk=report.pk).update(created_at=old_date)

        # Recalculate with 30 day max age - old report should be ignored
        ip.calculate_reputation(max_age_days=30)
        assert ip.reputation_score == 100

        # Recalculate with 60 day max age - old report should count
        ip.calculate_reputation(max_age_days=60)
        assert ip.reputation_score < 100
