"""
Unit tests for deepweb forms.
"""

from django.contrib.auth import get_user_model

import pytest

from deepweb.forms import (
    LoginForm,
    RegisterForm,
    ReportForm,
    SearchForm,
    UpdateProfileForm,
)
from deepweb.models import IPAddress, Report

from .factories import IPAddressFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestReportForm:
    """Tests for ReportForm."""

    def test_valid_ipv4_address(self):
        """Test form accepts valid IPv4 address."""
        form_data = {
            "ip_address": "192.168.1.1",
            "reason": "SPAM",
            "comment": "Test comment",
        }
        form = ReportForm(data=form_data)
        assert form.is_valid()

    def test_valid_ipv6_address(self):
        """Test form accepts valid IPv6 address."""
        form_data = {
            "ip_address": "2001:db8::1",
            "reason": "HACKING",
            "comment": "Test comment",
        }
        form = ReportForm(data=form_data)
        assert form.is_valid()

    def test_invalid_ip_address(self):
        """Test form rejects invalid IP address."""
        form_data = {
            "ip_address": "not-an-ip",
            "reason": "SPAM",
            "comment": "Test comment",
        }
        form = ReportForm(data=form_data)
        assert not form.is_valid()
        assert "ip_address" in form.errors
        assert len(form.errors["ip_address"]) > 0

    def test_missing_reason(self):
        """Test form requires reason field."""
        form_data = {
            "ip_address": "192.168.1.1",
            "comment": "Test comment",
        }
        form = ReportForm(data=form_data)
        assert not form.is_valid()
        assert "reason" in form.errors
        assert len(form.errors["reason"]) > 0

    def test_comment_optional(self):
        """Test comment field is optional."""
        form_data = {
            "ip_address": "192.168.1.1",
            "reason": "SPAM",
        }
        form = ReportForm(data=form_data)
        assert form.is_valid()

    def test_clean_ip_creates_new_ip(self):
        """Test clean_ip_address creates new IP if it doesn't exist."""
        form_data = {
            "ip_address": "10.0.0.99",
            "reason": "MALWARE",
            "comment": "New IP test",
        }
        form = ReportForm(data=form_data)
        assert form.is_valid()

        ip_obj = form.cleaned_data["ip_address"]
        assert isinstance(ip_obj, IPAddress)
        assert str(ip_obj.address) == "10.0.0.99"
        assert IPAddress.objects.filter(address="10.0.0.99").exists()

    def test_clean_ip_reuses_existing_ip(self):
        """Test clean_ip_address reuses existing IP."""
        existing_ip = IPAddressFactory(address="20.0.0.1")
        initial_count = IPAddress.objects.count()

        form_data = {
            "ip_address": "20.0.0.1",
            "reason": "PHISHING",
            "comment": "Existing IP test",
        }
        form = ReportForm(data=form_data)
        assert form.is_valid()

        assert IPAddress.objects.count() == initial_count
        ip_obj = form.cleaned_data["ip_address"]
        assert ip_obj.id == existing_ip.id

    def test_prefilled_ip_address(self):
        """Test form with prefilled IP address."""
        ip = IPAddressFactory(address="30.0.0.1")
        form = ReportForm(ip_address=ip.address)

        assert form.fields["ip_address"].initial == ip.address
        assert "ip_display" in form.fields

    def test_malformed_ipv4(self):
        """Test form rejects malformed IPv4."""
        form_data = {
            "ip_address": "999.999.999.999",
            "reason": "SPAM",
        }
        form = ReportForm(data=form_data)
        assert not form.is_valid()
        assert "ip_address" in form.errors
        assert len(form.errors["ip_address"]) > 0

    def test_malformed_ipv6(self):
        """Test form rejects malformed IPv6."""
        form_data = {
            "ip_address": "gggg:::::1",
            "reason": "SPAM",
        }
        form = ReportForm(data=form_data)
        assert not form.is_valid()
        assert "ip_address" in form.errors
        assert len(form.errors["ip_address"]) > 0

    def test_empty_ip_address(self):
        """Test form rejects empty IP address."""
        form_data = {
            "ip_address": "",
            "reason": "SPAM",
        }
        form = ReportForm(data=form_data)
        assert not form.is_valid()
        assert "ip_address" in form.errors
        assert len(form.errors["ip_address"]) > 0

    def test_all_reason_choices_valid(self):
        """Test all reason choices are accepted."""
        for reason_code, reason_label in Report.REASON_CHOICES:
            form_data = {
                "ip_address": f"40.0.0.{ord(reason_code[0])}",
                "reason": reason_code,
                "comment": f"Testing {reason_label}",
            }
            form = ReportForm(data=form_data)
            assert form.is_valid(), f"Reason {reason_code} should be valid"


@pytest.mark.django_db
@pytest.mark.unit
class TestRegisterForm:
    """Tests for RegisterForm."""

    def test_valid_registration(self):
        """Test form with valid registration data."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        form = RegisterForm(data=form_data)
        assert form.is_valid()

    def test_duplicate_active_email(self):
        """Test form rejects duplicate active email."""
        UserFactory(email="existing@example.com", is_active=True)

        form_data = {
            "username": "newuser",
            "email": "existing@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        form = RegisterForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors
        assert len(form.errors["email"]) > 0
        assert any(
            "actif" in str(err).lower() and "existe" in str(err).lower()
            for err in form.errors["email"]
        )

    def test_inactive_email_allowed(self):
        """Test form allows email from inactive account."""
        UserFactory(email="inactive@example.com", is_active=False)

        form_data = {
            "username": "newuser",
            "email": "inactive@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        form = RegisterForm(data=form_data)
        form.is_valid()
        assert "email" not in form.errors

    def test_password_mismatch(self):
        """Test form rejects mismatched passwords."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "testpass123!",
            "password2": "different123!",
        }
        form = RegisterForm(data=form_data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_missing_email(self):
        """Test form requires email."""
        form_data = {
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        form = RegisterForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_invalid_email_format(self):
        """Test form rejects invalid email format."""
        form_data = {
            "username": "newuser",
            "email": "not-an-email",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        form = RegisterForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_missing_first_name(self):
        """Test form requires first name."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "last_name": "Doe",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        form = RegisterForm(data=form_data)
        assert not form.is_valid()
        assert "first_name" in form.errors

    def test_missing_last_name(self):
        """Test form requires last name."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "John",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        form = RegisterForm(data=form_data)
        assert not form.is_valid()
        assert "last_name" in form.errors

    def test_save_creates_new_user(self):
        """Test save() creates new active user."""
        form_data = {
            "username": "brandnew",
            "email": "brandnew@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        form = RegisterForm(data=form_data)
        assert form.is_valid()

        user = form.save()
        assert user.username == "brandnew"
        assert user.email == "brandnew@example.com"
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"
        assert user.is_active is True
        assert user.check_password("testpass123!")

    def test_save_reactivates_inactive_user(self):
        """Test save() reactivates inactive user with same email."""
        inactive_user = UserFactory(
            username="olduser",
            email="reactivate@example.com",
            is_active=False,
            first_name="Old",
            last_name="Name",
        )
        inactive_user.set_password("oldpass")
        inactive_user.save()

        form_data = {
            "username": "newusername",
            "email": "reactivate@example.com",
            "first_name": "New",
            "last_name": "Name",
            "password1": "newpass123!",
            "password2": "newpass123!",
        }
        form = RegisterForm(data=form_data)
        assert form.is_valid()

        user = form.save()
        assert user.id == inactive_user.id
        assert user.username == "newusername"
        assert user.email == "reactivate@example.com"
        assert user.first_name == "New"
        assert user.last_name == "Name"
        assert user.is_active is True
        assert user.check_password("newpass123!")


@pytest.mark.unit
class TestLoginForm:
    """Tests for LoginForm."""

    def test_valid_credentials(self):
        form_data = {
            "username": "testuser",
            "password": "testpass123",
        }
        form = LoginForm(data=form_data)
        assert form.is_valid()

    def test_missing_username(self):
        form = LoginForm(data={"password": "testpass123"})
        assert not form.is_valid()
        assert "username" in form.errors
        assert len(form.errors["username"]) > 0

    def test_missing_password(self):
        form = LoginForm(data={"username": "testuser"})
        assert not form.is_valid()
        assert "password" in form.errors
        assert len(form.errors["password"]) > 0

    def test_empty_form(self):
        form = LoginForm(data={})
        assert not form.is_valid()
        assert len(form.errors) == 2


@pytest.mark.unit
class TestSearchForm:
    """Tests for SearchForm."""

    def test_valid_search(self):
        form = SearchForm(
            data={
                "recherche": "192.168.1.1",
                "tries": "default",
                "filtres": "4",
            }
        )
        assert form.is_valid()

    def test_all_fields_optional(self):
        form = SearchForm(data={})
        assert form.is_valid()

    def test_ipv6_filter(self):
        form = SearchForm(data={"filtres": "6"})
        assert form.is_valid()
        assert form.cleaned_data["filtres"] == "6"

    def test_ipv4_filter(self):
        form = SearchForm(data={"filtres": "4"})
        assert form.is_valid()
        assert form.cleaned_data["filtres"] == "4"

    def test_sort_choices(self):
        sort_options = [
            "default",
            "reputationDesc",
            "reputationAsc",
            "modificationDesc",
        ]
        for sort_option in sort_options:
            form = SearchForm(data={"tries": sort_option})
            assert form.is_valid()
            assert form.cleaned_data["tries"] == sort_option

    def test_search_with_ip(self):
        form = SearchForm(data={"recherche": "10.0.0.1"})
        assert form.is_valid()
        assert form.cleaned_data["recherche"] == "10.0.0.1"


@pytest.mark.django_db
@pytest.mark.unit
class TestUpdateProfileForm:
    """Tests for UpdateProfileForm."""

    def test_valid_profile_update(self):
        """Test form with valid profile update data."""
        form_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
        }
        form = UpdateProfileForm(data=form_data)
        assert form.is_valid()

    def test_valid_profile_update_with_password(self):
        """Test form with valid profile update including password change."""
        form_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "password": "newpass123!",
            "password_confirm": "newpass123!",
        }
        form = UpdateProfileForm(data=form_data)
        assert form.is_valid()

    def test_password_optional(self):
        """Test password fields are optional."""
        form_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
        }
        form = UpdateProfileForm(data=form_data)
        assert form.is_valid()

    def test_missing_email(self):
        """Test form requires email."""
        form_data = {
            "first_name": "Jane",
            "last_name": "Doe",
        }
        form = UpdateProfileForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_invalid_email_format(self):
        """Test form rejects invalid email format."""
        form_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "not-an-email",
        }
        form = UpdateProfileForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_missing_first_name(self):
        """Test form requires first name."""
        form_data = {
            "last_name": "Doe",
            "email": "jane.doe@example.com",
        }
        form = UpdateProfileForm(data=form_data)
        assert not form.is_valid()
        assert "first_name" in form.errors

    def test_missing_last_name(self):
        """Test form requires last name."""
        form_data = {
            "first_name": "Jane",
            "email": "jane.doe@example.com",
        }
        form = UpdateProfileForm(data=form_data)
        assert not form.is_valid()
        assert "last_name" in form.errors

    def test_email_min_length(self):
        """Test email has minimum length validation."""
        form_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "a@b",  # Less than 5 characters
        }
        form = UpdateProfileForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors
