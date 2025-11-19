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
        assert r1.id and r2.id  # Use variables to avoid flake8 warnings
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
        ReportFactory(ip_address=ip, user=user)
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


@pytest.mark.django_db
class TestAuthenticationViews:
    """Tests for login/logout views."""

    def test_login_success(self, client, user_factory):
        user = user_factory(username="testuser")
        user.set_password("testpass123")
        user.save()

        response = client.post(
            reverse("connecter"),
            {"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 302
        assert client.session["_auth_user_id"]

    def test_login_invalid_credentials(self, client, user_factory):
        user = user_factory(username="testuser")
        user.set_password("testpass123")
        user.save()

        response = client.post(
            reverse("connecter"),
            {"username": "testuser", "password": "wrongpass"},
        )
        assert response.status_code == 200
        assert "_auth_user_id" not in client.session

    def test_logout(self, client, user_factory):
        user = user_factory()
        client.force_login(user)
        response = client.get(reverse("deconnecter"))
        assert response.status_code == 302
        assert "_auth_user_id" not in client.session


@pytest.mark.django_db
class TestStatisticsView:
    """Tests for statistics page."""

    def test_statistics_page_loads(self, client):
        response = client.get(reverse("statistics"))
        assert response.status_code == 200

    def test_statistics_with_data(self, client, report_factory):
        report_factory.create_batch(5)
        response = client.get(reverse("statistics"))
        assert response.status_code == 200
        assert b"Statistiques" in response.content


@pytest.mark.django_db
class TestIndexView:
    """Tests for index page."""

    def test_index_loads(self, client):
        response = client.get(reverse("index"))
        assert response.status_code == 200

    def test_index_shows_recent_reports(self, client, report_factory):
        report_factory.create_batch(3)
        response = client.get(reverse("index"))
        assert response.status_code == 200
        assert b"BlockList" in response.content


@pytest.mark.django_db
class TestReportIPView:
    """Tests for report_ip view."""

    def test_report_ip_requires_login(self, client):
        response = client.get(reverse("report_ip"))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_report_ip_form_loads(self, client, user_factory):
        user = user_factory()
        client.force_login(user)
        response = client.get(reverse("report_ip"))
        assert response.status_code == 200

    def test_create_report_for_new_ip(self, client, user_factory):
        user = user_factory()
        client.force_login(user)

        response = client.post(
            reverse("report_ip"),
            {
                "ip_address": "8.8.8.8",
                "reason": "SPAM",
                "comment": "Test report",
            },
        )
        assert response.status_code == 302
        assert Report.objects.filter(ip_address__address="8.8.8.8").exists()

    def test_create_report_for_existing_ip(
        self, client, user_factory, ip_address_factory
    ):
        user = user_factory()
        client.force_login(user)
        ip = ip_address_factory(address="1.2.3.4")

        response = client.post(
            reverse("report_ip", kwargs={"ip_address": ip.address}),
            {
                "ip_address": ip.address,
                "reason": "HACKING",
                "comment": "Suspicious activity",
            },
        )
        assert response.status_code == 302
        assert Report.objects.filter(ip_address=ip, user=user).exists()


@pytest.mark.django_db
class TestIPDetailView:
    """Tests for ip_detail view."""

    def test_ip_detail_loads(self, client, ip_address_factory):
        ip = ip_address_factory(address="10.0.0.1")
        response = client.get(reverse("ip_detail", kwargs={"ip_address": ip.address}))
        assert response.status_code == 200
        assert b"10.0.0.1" in response.content

    def test_ip_detail_with_reports(self, client, ip_address_factory, report_factory):
        ip = ip_address_factory(address="10.0.0.2")
        report_factory.create_batch(3, ip_address=ip)

        response = client.get(reverse("ip_detail", kwargs={"ip_address": ip.address}))
        assert response.status_code == 200
        assert b"Historique des signalements" in response.content

    def test_ip_detail_invalid_ip(self, client):
        response = client.get(reverse("ip_detail", kwargs={"ip_address": "invalid"}))
        assert response.status_code == 404

    def test_ip_detail_with_zero_reports(self, client, ip_address_factory):
        """Test IP detail with no reports (edge case for JavaScript)."""
        ip = ip_address_factory(address="192.168.1.1")
        response = client.get(reverse("ip_detail", kwargs={"ip_address": ip.address}))

        assert response.status_code == 200
        assert b"Aucun signalement" in response.content
        # Ensure reports-tbody doesn't exist when no reports
        assert b'id="reports-tbody"' not in response.content


@pytest.mark.django_db
class TestRechercherView:
    """Tests for search view."""

    def test_search_by_ip(self, client, ip_address_factory):
        ip_address_factory(address="192.168.1.1")

        response = client.post(
            reverse("rechercher"),
            {"recherche": "192.168.1.1"},
        )
        assert response.status_code == 200

    def test_search_with_filters(self, client, ip_address_factory):
        ip_address_factory(address="192.168.1.1")
        ip_address_factory(address="2001:db8::1")

        response = client.post(
            reverse("rechercher"),
            {"recherche": "", "filtres": "4"},
        )
        assert response.status_code == 200
