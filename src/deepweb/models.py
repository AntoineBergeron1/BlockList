import ipaddress
import socket

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

# Create your models here.


class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/")
    bio = models.TextField(max_length=500)


class Category(models.Model):
    nom = models.CharField(max_length=100)
    description = models.CharField(max_length=300, default="")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom


class IPAddress(models.Model):
    """
    Model representing an individual IP address (IPv4 or IPv6) with reputation tracking.
    GenericIPAddressField automatically uses PostgreSQL INET type for native IP operations.
    """

    IPV4 = 4
    IPV6 = 6
    IP_VERSION_CHOICES = [
        (IPV4, "IPv4"),
        (IPV6, "IPv6"),
    ]

    address = models.GenericIPAddressField(unique=True, verbose_name="Adresse IP")
    version = models.IntegerField(choices=IP_VERSION_CHOICES, verbose_name="Version")
    hostname = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Nom de domaine"
    )
    reputation_score = models.IntegerField(
        default=100, verbose_name="Score de réputation"
    )

    # GeoIP2 enrichment fields
    country_code = models.CharField(
        max_length=2, blank=True, null=True, verbose_name="Code pays (ISO)"
    )
    country_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Pays"
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville")
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Latitude"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Longitude"
    )
    asn = models.IntegerField(blank=True, null=True, verbose_name="ASN")
    asn_organization = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Organisation ASN"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Adresse IP"
        verbose_name_plural = "Adresses IP"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["address"]),
            models.Index(fields=["-reputation_score"]),
        ]
        # Enable GiST index for INET operations in PostgreSQL
        # Run: CREATE INDEX CONCURRENTLY idx_ipaddress_gist ON deepweb_ipaddress USING gist (address inet_ops);

    def __str__(self):
        return str(self.address)

    def clean(self):
        """
        Validate IP address and automatically detect version.
        """
        if self.address:
            try:
                ip_obj = ipaddress.ip_address(str(self.address))
                self.version = self.IPV4 if ip_obj.version == 4 else self.IPV6
            except ValueError:
                raise ValidationError({"address": "Adresse IP invalide."})

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation runs.
        """
        self.clean()
        super().save(*args, **kwargs)

    def calculate_reputation(self):
        """
        Calculate reputation score based on reports.
        Base score: 100
        Each report decreases the score (weighted by severity).
        """
        reports = self.reports.all()
        total_reports = reports.count()

        if total_reports == 0:
            self.reputation_score = 100
        else:
            # Basic calculation: lose 5 points per report, minimum 0
            self.reputation_score = max(0, 100 - (total_reports * 5))

        self.save()
        return self.reputation_score

    def lookup_hostname(self):
        """
        Perform reverse DNS lookup to retrieve hostname for this IP address.
        Returns the hostname if found, None otherwise.
        Updates the hostname field and saves the instance.
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(str(self.address))
            self.hostname = hostname
            self.save(update_fields=["hostname"])
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout):
            # No reverse DNS record found or lookup failed
            self.hostname = None
            self.save(update_fields=["hostname"])
            return None

    def enrich_geoip(self):
        """
        Enrich IP address with GeoIP2 data (country, city, coordinates, ASN).
        Requires GeoLite2 databases to be downloaded in GEOIP_PATH.
        """
        try:
            from django.contrib.gis.geoip2 import GeoIP2

            g = GeoIP2()
            ip_str = str(self.address)

            # City data (includes country, city, coordinates)
            try:
                city_data = g.city(ip_str)
                if city_data:
                    self.country_code = city_data.get("country_code")
                    self.country_name = city_data.get("country_name")
                    self.city = city_data.get("city")
                    if "latitude" in city_data and "longitude" in city_data:
                        self.latitude = city_data["latitude"]
                        self.longitude = city_data["longitude"]
            except Exception:
                pass

            # ASN data (requires GeoLite2-ASN.mmdb)
            try:
                from django.conf import settings

                import geoip2.database

                asn_db_path = settings.GEOIP_PATH / "GeoLite2-ASN.mmdb"
                with geoip2.database.Reader(str(asn_db_path)) as reader:
                    asn_data = reader.asn(ip_str)
                    self.asn = asn_data.autonomous_system_number
                    self.asn_organization = asn_data.autonomous_system_organization
            except Exception:
                pass

            self.save(
                update_fields=[
                    "country_code",
                    "country_name",
                    "city",
                    "latitude",
                    "longitude",
                    "asn",
                    "asn_organization",
                ]
            )
            return True
        except Exception:
            return False


class Report(models.Model):
    """
    Model representing a report/signalement for an IP address.
    """

    # Temporary reason choices (will be refined later)
    SPAM = "SPAM"
    HACKING = "HACKING"
    WEB_APP_ATTACK = "WEB_APP_ATTACK"
    PORT_SCAN = "PORT_SCAN"
    MALWARE = "MALWARE"
    PHISHING = "PHISHING"
    BRUTE_FORCE = "BRUTE_FORCE"
    DDoS = "DDoS"
    OTHER = "OTHER"

    REASON_CHOICES = [
        (SPAM, "Spam"),
        (HACKING, "Hacking"),
        (WEB_APP_ATTACK, "Attaque d'application web"),
        (PORT_SCAN, "Scan de ports"),
        (MALWARE, "Logiciel malveillant"),
        (PHISHING, "Hameçonnage"),
        (BRUTE_FORCE, "Attaque par force brute"),
        (DDoS, "Attaque DDoS"),
        (OTHER, "Autre"),
    ]

    ip_address = models.ForeignKey(
        IPAddress,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="Adresse IP",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="Utilisateur",
    )
    reason = models.CharField(
        max_length=50, choices=REASON_CHOICES, verbose_name="Raison"
    )
    comment = models.TextField(max_length=1000, blank=True, verbose_name="Commentaire")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.ip_address.address} ({self.get_reason_display()})"

    def save(self, *args, **kwargs):
        """
        Override save to recalculate IP reputation after creating a report.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Recalculate reputation after new report
            self.ip_address.calculate_reputation()


class CIDRField(models.Field):
    """
    Custom field for PostgreSQL CIDR type.
    Stores IP network ranges (e.g., 192.168.1.0/24, 2001:db8::/32).
    """

    description = "PostgreSQL CIDR network field"

    def db_type(self, connection):
        return "cidr"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return str(value)

    def to_python(self, value):
        if value is None or value == "":
            return value
        if isinstance(value, str):
            try:
                # Validate CIDR notation
                ipaddress.ip_network(value, strict=False)
                return value
            except ValueError as e:
                raise ValidationError(f"Format CIDR invalide: {e}")
        return str(value)

    def get_prep_value(self, value):
        if value is None:
            return None
        return str(value)


class IPRange(models.Model):
    """
    Model representing IP address ranges/networks using CIDR notation.
    Uses PostgreSQL CIDR type for efficient subnet matching and range operations.
    Useful for blocking entire networks (botnets, cloud providers, etc.)
    """

    network = CIDRField(unique=True, verbose_name="Réseau CIDR")
    description = models.CharField(max_length=500, verbose_name="Description")
    is_blocked = models.BooleanField(default=False, verbose_name="Bloqué")
    severity = models.IntegerField(
        default=50, verbose_name="Sévérité", help_text="Niveau de dangerosité (0-100)"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_ranges",
        verbose_name="Créé par",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Plage IP"
        verbose_name_plural = "Plages IP"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_blocked"]),
        ]
        # Enable GiST index for CIDR operations in PostgreSQL
        # Run: CREATE INDEX CONCURRENTLY idx_iprange_gist ON deepweb_iprange USING gist (network inet_ops);

    def __str__(self):
        return f"{self.network} - {self.description[:50]}"

    def clean(self):
        """
        Validate CIDR network format.
        """
        if self.network:
            try:
                ipaddress.ip_network(self.network, strict=False)
            except ValueError as e:
                raise ValidationError({"network": f"Format CIDR invalide: {e}"})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def contains_ip(self, ip_str):
        """
        Check if an IP address is within this CIDR range.
        Uses Python ipaddress for validation (can be optimized with PostgreSQL << operator).
        """
        try:
            ip = ipaddress.ip_address(ip_str)
            network = ipaddress.ip_network(self.network, strict=False)
            return ip in network
        except ValueError:
            return False
