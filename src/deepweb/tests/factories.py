"""
Factory Boy factories for creating test data.
"""
import factory
from factory.django import DjangoModelFactory
from deepweb.models import User, IPAddress, Report


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True


class IPAddressFactory(DjangoModelFactory):
    """Factory for creating IPAddress instances."""

    class Meta:
        model = IPAddress

    address = factory.Faker("ipv4")
    version = IPAddress.IPV4
    reputation_score = 100


class ReportFactory(DjangoModelFactory):
    """Factory for creating Report instances."""

    class Meta:
        model = Report

    ip_address = factory.SubFactory(IPAddressFactory)
    user = factory.SubFactory(UserFactory)
    reason = Report.SPAM
    comment = factory.Faker("text", max_nb_chars=200)
