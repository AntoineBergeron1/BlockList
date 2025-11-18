from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create test users for development"

    def handle(self, *args, **options):
        # Create regular user
        if not User.objects.filter(username="user").exists():
            User.objects.create_user(
                username="user",
                email="user@example.com",
                password="user123",
                first_name="Test",
                last_name="User",
            )
            self.stdout.write(self.style.SUCCESS("✓ Created test user: user / user123"))
        else:
            self.stdout.write(self.style.WARNING("Test user already exists"))

        # Create admin user
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123",
                first_name="Admin",
                last_name="User",
            )
            self.stdout.write(
                self.style.SUCCESS("✓ Created admin user: admin / admin123")
            )
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists"))
