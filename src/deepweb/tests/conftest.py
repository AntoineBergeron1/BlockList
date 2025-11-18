"""
Pytest configuration and fixtures for deepweb app tests.
"""

import pytest
from pytest_factoryboy import register

from .factories import IPAddressFactory, ReportFactory, UserFactory

# Register factories as fixtures
register(UserFactory)
register(IPAddressFactory)
register(ReportFactory)
