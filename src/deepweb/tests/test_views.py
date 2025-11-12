"""
Tests for views, including chart API endpoint.
"""

from django.urls import reverse

import pytest

from deepweb.models import Report

from .factories import IPAddressFactory, ReportFactory, UserFactory


@pytest.mark.django_db
class TestIPChartDataAPI:
    """Tests for ip_chart_data API endpoint."""

    def test_chart_data_with_no_reports(self, client):
        """Test API returns empty datasets when IP has no reports."""
        ip = IPAddressFactory(address="1.2.3.4")
        url = reverse("ip_chart_data", kwargs={"ip_address": ip.address})

        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["timeline"]["labels"] == []
        assert data["timeline"]["data"] == []
        assert data["threatTypes"]["labels"] == []
        assert data["topUsers"]["labels"] == []

    def test_chart_data_with_reports(self, client):
        """Test API returns correct data structure with reports."""
        ip = IPAddressFactory(address="5.6.7.8")
        user1 = UserFactory(username="user1")
        user2 = UserFactory(username="user2")

        # Create reports
        ReportFactory(ip_address=ip, user=user1, reason=Report.SPAM, comment="Test 1")
        ReportFactory(
            ip_address=ip, user=user2, reason=Report.HACKING, comment="Test 2"
        )
        ReportFactory(ip_address=ip, user=user1, reason=Report.SPAM, comment="Test 3")

        url = reverse("ip_chart_data", kwargs={"ip_address": ip.address})
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()

        # Timeline should have data
        assert len(data["timeline"]["labels"]) > 0
        assert len(data["timeline"]["data"]) > 0
        assert sum(data["timeline"]["data"]) == 3

        # Threat types should show SPAM (2) and HACKING (1)
        assert len(data["threatTypes"]["labels"]) == 2
        assert "Spam" in data["threatTypes"]["labels"]
        assert "Hacking" in data["threatTypes"]["labels"]

        # Top users should have user1 and user2
        assert len(data["topUsers"]["labels"]) == 2
        assert "user1" in data["topUsers"]["labels"]
        assert "user2" in data["topUsers"]["labels"]

    def test_chart_data_invalid_ip(self, client):
        """Test API returns 400 for invalid IP address."""
        url = reverse("ip_chart_data", kwargs={"ip_address": "invalid-ip"})
        response = client.get(url)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "Adresse IP invalide"

    def test_chart_data_nonexistent_ip(self, client):
        """Test API returns 404 for non-existent IP."""
        url = reverse("ip_chart_data", kwargs={"ip_address": "192.168.99.99"})
        response = client.get(url)

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"] == "IP non trouvée"

    def test_chart_data_top_users_limit(self, client):
        """Test API limits top users to 5."""
        ip = IPAddressFactory(address="20.0.0.1")

        # Create 7 users with different report counts
        for i in range(7):
            user = UserFactory(username=f"user{i}")
            for _ in range(i + 1):
                ReportFactory(ip_address=ip, user=user)

        url = reverse("ip_chart_data", kwargs={"ip_address": ip.address})
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()

        # Should only return top 5 users
        assert len(data["topUsers"]["labels"]) == 5
        # Top user should be user6 (7 reports)
        assert data["topUsers"]["labels"][0] == "user6"
        assert data["topUsers"]["data"][0] == 7


@pytest.mark.django_db
class TestIPReportsAPI:
    """Tests for ip_reports_api endpoint (AJAX live updates)."""

    def test_reports_api_no_reports(self, client):
        """Test API returns empty list when IP has no reports."""
        ip = IPAddressFactory(address="10.0.0.1")
        url = reverse("ip_reports_api", kwargs={"ip_address": ip.address})

        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["reports"] == []
        assert data["count"] == 0
        assert data["latest_id"] is None

    def test_reports_api_with_reports(self, client):
        """Test API returns all reports for an IP."""
        ip = IPAddressFactory(address="10.0.0.2")
        user = UserFactory(username="testuser")

        # Create 3 reports
        r1 = ReportFactory(ip_address=ip, user=user, reason=Report.SPAM)
        r2 = ReportFactory(ip_address=ip, user=user, reason=Report.HACKING)
        r3 = ReportFactory(ip_address=ip, user=user, reason=Report.MALWARE)

        url = reverse("ip_reports_api", kwargs={"ip_address": ip.address})
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert data["latest_id"] == r3.id
        assert len(data["reports"]) == 3

        # Check report structure
        first_report = data["reports"][0]
        assert "id" in first_report
        assert "user" in first_report
        assert "date" in first_report
        assert "date_iso" in first_report
        assert "time_since" in first_report
        assert "comment" in first_report
        assert "reason" in first_report

    def test_reports_api_with_since_id(self, client):
        """Test API returns only reports newer than since_id."""
        ip = IPAddressFactory(address="10.0.0.3")
        user = UserFactory(username="testuser")

        # Create 5 reports
        r1 = ReportFactory(ip_address=ip, user=user, reason=Report.SPAM)
        r2 = ReportFactory(ip_address=ip, user=user, reason=Report.HACKING)
        r3 = ReportFactory(ip_address=ip, user=user, reason=Report.MALWARE)
        r4 = ReportFactory(ip_address=ip, user=user, reason=Report.PHISHING)
        r5 = ReportFactory(ip_address=ip, user=user, reason=Report.DDoS)

        # Query for reports after r2
        url = reverse("ip_reports_api", kwargs={"ip_address": ip.address})
        response = client.get(url, {"since_id": r2.id})

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3  # r3, r4, r5
        assert data["latest_id"] == r5.id

        # Verify only newer reports are returned
        report_ids = [r["id"] for r in data["reports"]]
        assert r3.id in report_ids
        assert r4.id in report_ids
        assert r5.id in report_ids
        assert r1.id not in report_ids
        assert r2.id not in report_ids

    def test_reports_api_no_new_reports(self, client):
        """Test API returns empty when no reports newer than since_id."""
        ip = IPAddressFactory(address="10.0.0.4")
        user = UserFactory(username="testuser")

        # Create 2 reports
        r1 = ReportFactory(ip_address=ip, user=user)
        r2 = ReportFactory(ip_address=ip, user=user)

        # Query for reports after the latest one
        url = reverse("ip_reports_api", kwargs={"ip_address": ip.address})
        response = client.get(url, {"since_id": r2.id})

        assert response.status_code == 200
        data = response.json()
        assert data["reports"] == []
        assert data["count"] == 0
        assert data["latest_id"] is None

    def test_reports_api_invalid_ip(self, client):
        """Test API returns 400 for invalid IP address."""
        url = reverse("ip_reports_api", kwargs={"ip_address": "not-an-ip"})
        response = client.get(url)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "Adresse IP invalide"

    def test_reports_api_nonexistent_ip(self, client):
        """Test API returns empty for non-existent IP."""
        url = reverse("ip_reports_api", kwargs={"ip_address": "192.168.88.88"})
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["reports"] == []
        assert data["count"] == 0

    def test_reports_api_invalid_since_id(self, client):
        """Test API returns 400 for invalid since_id parameter."""
        ip = IPAddressFactory(address="10.0.0.5")
        url = reverse("ip_reports_api", kwargs={"ip_address": ip.address})
        response = client.get(url, {"since_id": "not-a-number"})

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_reports_api_limit_10(self, client):
        """Test API limits results to 10 reports."""
        ip = IPAddressFactory(address="10.0.0.6")
        user = UserFactory(username="testuser")

        # Create 15 reports
        for _ in range(15):
            ReportFactory(ip_address=ip, user=user)

        url = reverse("ip_reports_api", kwargs={"ip_address": ip.address})
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        # Should only return 10 most recent
        assert data["count"] == 10
        assert len(data["reports"]) == 10

    def test_reports_api_ordered_by_newest(self, client):
        """Test API returns reports ordered by creation date (newest first)."""
        ip = IPAddressFactory(address="10.0.0.7")
        user = UserFactory(username="testuser")

        # Create 3 reports
        r1 = ReportFactory(ip_address=ip, user=user, comment="First")
        r2 = ReportFactory(ip_address=ip, user=user, comment="Second")
        r3 = ReportFactory(ip_address=ip, user=user, comment="Third")

        url = reverse("ip_reports_api", kwargs={"ip_address": ip.address})
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()

        # First report in response should be the most recent (r3)
        assert data["reports"][0]["id"] == r3.id
        assert data["reports"][1]["id"] == r2.id
        assert data["reports"][2]["id"] == r1.id
