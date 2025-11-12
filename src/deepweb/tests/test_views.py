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
