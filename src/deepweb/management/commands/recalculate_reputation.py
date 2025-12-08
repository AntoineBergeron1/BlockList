"""
Management command to recalculate reputation scores for all IP addresses.
Should be run daily via cron job to apply time decay.

Usage:
    python manage.py recalculate_reputation
    python manage.py recalculate_reputation --max-age=60
"""

from django.core.management.base import BaseCommand

from deepweb.models import IPAddress


class Command(BaseCommand):
    help = "Recalculate reputation scores for all IP addresses with time decay"

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-age",
            type=int,
            default=30,
            help="Maximum age of reports in days (default: 30)",
        )

    def handle(self, *args, **options):
        max_age_days = options["max_age"]

        # Get all IPs that have at least one report
        ips_with_reports = IPAddress.objects.filter(reports__isnull=False).distinct()
        total_ips = ips_with_reports.count()

        self.stdout.write(
            f"Recalculating reputation for {total_ips} IPs "
            f"(max age: {max_age_days} days)..."
        )

        updated_count = 0
        for ip in ips_with_reports:
            old_score = ip.reputation_score
            new_score = ip.calculate_reputation(max_age_days=max_age_days)

            if old_score != new_score:
                updated_count += 1
                self.stdout.write(
                    f"  {ip.address}: {old_score} -> {new_score}",
                    self.style.SUCCESS if new_score > old_score else self.style.WARNING,
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Updated {updated_count}/{total_ips} IP reputation scores."
            )
        )
