import ipaddress
import os
from datetime import datetime, timedelta
from multiprocessing import managers

from django.conf import (  # TODO: Used for DEBUG in login view quick-login buttons
    settings,
)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage
from django.db.models import CharField, Count, F, Max, Min
from django.db.models.functions import Cast, TruncDate, TruncHour
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timesince import timesince
import json
from .forms import LoginForm, RegisterForm, ReportForm, SearchForm, UpdateProfileForm
from .models import IPAddress, Report, User

utilisateurs = User.objects.all()
lesIps = IPAddress.objects.all()
reports = Report.objects.all()

# Create your views here.


def index(request):
    """Voir les dernières ip reportées sur la page accueil"""
    recent_reports = Report.objects.all().order_by("-created_at")[:9]

    form = SearchForm()
    return render(
        request,
        "deepweb/index.html",
        {
            "form": form,
            "results": IPAddress.objects.all().order_by("-created_at"),
            "reports": reports,
            "recent_reports": recent_reports,
        },
    )


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(username=username)
                if not user.is_active:
                    if check_password(password, user.password):
                        user.is_active = True
                        user.email = email
                        user.save()
                        messages.success(request, "Compte réactivé avec succès !")
                        login(request, user)
                        return redirect("connecter")
                    else:
                        messages.error(
                            request, "Mot de passe incorrect pour réactivation."
                        )
                        return render(request, "deepweb/register.html", {"form": form})
                else:
                    messages.error(request, "Nom d'utilisateur déjà pris.")
                    return render(request, "deepweb/register.html", {"form": form})
            except User.DoesNotExist:
                user = form.save()
                login(request, user)
                messages.success(request, "Compte créé avec succès !")
                return redirect("connecter")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = RegisterForm()
    return render(request, "deepweb/register.html", {"form": form})


def connecter(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Connecté avec succès !")
                return redirect("index")
            else:
                form.add_error(None, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = LoginForm()

    return render(
        request, "deepweb/login.html", {"form": form, "debug": settings.DEBUG}
    )


def deconnecter(request):
    logout(request)
    messages.success(request, "Déconnecté avec succès !")
    return redirect("index")


def ip_detail(request, ip_address):
    """
    Display IP address details with reports history.
    Shows first 10 reports, with AJAX load more functionality.
    Creates IP if it doesn't exist (useful for checking new IPs).
    """
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        raise Http404("Adresse IP invalide")

    ip_obj, created = IPAddress.objects.get_or_create(address=ip_address)

    # Perform reverse DNS lookup if hostname is not set
    if not ip_obj.hostname:
        ip_obj.lookup_hostname()

    # Enrich with GeoIP data if not already enriched
    if not ip_obj.country_code and not ip_obj.asn:
        ip_obj.enrich_geoip()

    # Get reports with statistics
    reports = ip_obj.reports.select_related("user").order_by("-created_at")

    # Calculate statistics
    total_reports = reports.count()
    first_report_date = reports.aggregate(Min("created_at"))["created_at__min"]
    last_report_date = reports.aggregate(Max("created_at"))["created_at__max"]

    # Get first 10 reports for initial load
    initial_reports = reports[:10]

    context = {
        "ip_address": ip_obj,
        "reports": initial_reports,
        "total_reports": total_reports,
        "first_report_date": first_report_date,
        "last_report_date": last_report_date,
        "has_more": total_reports > 10,
        "is_new": created,
    }

    return render(request, "deepweb/ip_detail.html", context)


def ip_reports_api(request, ip_address):
    """
    API endpoint to fetch latest reports for an IP address.
    Supports polling with 'since_id' parameter for real-time updates.
    Returns JSON with new reports since the given ID.
    """
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return JsonResponse({"error": "Adresse IP invalide"}, status=400)

    try:
        ip_obj = IPAddress.objects.get(address=ip_address)
    except IPAddress.DoesNotExist:
        return JsonResponse({"reports": [], "count": 0})

    # Get 'since_id' parameter to fetch only new reports
    since_id = request.GET.get("since_id")

    # Build query
    reports_query = ip_obj.reports.select_related("user").order_by("-created_at")

    # Filter by since_id if provided (for polling)
    if since_id:
        try:
            reports_query = reports_query.filter(id__gt=int(since_id))
        except ValueError:
            return JsonResponse({"error": "Invalid since_id parameter"}, status=400)

    # Limit to last 10 new reports
    reports = reports_query[:10]

    # Serialize reports
    reports_data = [
        {
            "id": report.id,
            "user": report.user.username,
            "date": report.created_at.strftime("%Y-%m-%d %H:%M"),
            "date_iso": report.created_at.isoformat(),
            "time_since": f"il y a {timesince(report.created_at)}",
            "comment": report.comment or "",
            "reason": report.get_reason_display(),
        }
        for report in reports
    ]

    all_reports = ip_obj.reports.all()
    total_count = all_reports.count()
    first_date = all_reports.aggregate(Min("created_at"))["created_at__min"]
    last_date = all_reports.aggregate(Max("created_at"))["created_at__max"]

    return JsonResponse(
        {
            "reports": reports_data,
            "count": len(reports_data),
            "latest_id": reports_data[0]["id"] if reports_data else None,
            "statistics": {
                "total_reports": total_count,
                "first_report_date": (
                    first_date.strftime("%d/%m/%Y") if first_date else "N/A"
                ),
                "last_report_date": (
                    last_date.strftime("%d/%m/%Y") if last_date else "N/A"
                ),
            },
            "ip_info": {
                "reputation_score": ip_obj.reputation_score,
                "created_at": ip_obj.created_at.strftime("%d/%m/%Y %H:%M"),
                "updated_at": ip_obj.updated_at.strftime("%d/%m/%Y %H:%M"),
            },
        }
    )


@login_required
def report_ip(request, ip_address=None):
    """
    Form to report an IP address.
    If ip_address is provided, pre-fill the IP address (readonly).
    Creates IP if it doesn't exist.
    """
    ip_obj = None
    if ip_address:
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            raise Http404("Adresse IP invalide")
        ip_obj, created = IPAddress.objects.get_or_create(address=ip_address)

    if request.method == "POST":
        form = ReportForm(request.POST, ip_address=ip_obj.address if ip_obj else None)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()

            messages.success(
                request,
                f"Signalement enregistré avec succès pour l'IP {report.ip_address.address}!",
            )
            return redirect("ip_detail", ip_address=report.ip_address.address)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ReportForm(ip_address=ip_obj.address if ip_obj else None)

    context = {
        "form": form,
        "ip_address": ip_obj,
    }

    return render(request, "deepweb/report_form.html", context)


@login_required
def list_user(request):
    """Liste utilisateurs"""
    user = request.user
    utilisateurs = User.objects.all().order_by("username")

    if not request.user.is_staff:
        return render(request, "deepweb/403.html")

    return render(
        request, "deepweb/list_user.html", {"utilisateurs": utilisateurs, "user": user}
    )


@login_required
def list_user_update(request, pk):
    """Liste utilisateurs mise a jour"""
    utilisateur = get_object_or_404(User, id=pk)

    if request.method == "POST":
        utilisateur.is_staff = "is_staff" in request.POST
        utilisateur.is_active = "is_active" in request.POST
        utilisateur.save()

    return redirect("list_user")


def rechercher(request):
    if request.method == "POST":
        recent_reports = Report.objects.all().order_by("-created_at")[:9]

        form = SearchForm(request.POST)
        if form.is_valid():

            versionSelectionnee = form.cleaned_data.get("filtres")
            resultat_recherche = form.cleaned_data["recherche"]
            optiontri = form.cleaned_data.get("tries")
            if resultat_recherche:
                results = IPAddress.objects.annotate(
                    addr_str=Cast(F("address"), output_field=CharField())
                ).filter(addr_str__icontains=resultat_recherche)
            else:
                results = IPAddress.objects.all()

            if versionSelectionnee:
                results = results.filter(version=versionSelectionnee)
                print(versionSelectionnee)

            if optiontri == "reputationDesc":
                results = results.order_by("-reputation_score")
            elif optiontri == "reputationAsc":
                results = results.order_by("reputation_score")
            elif optiontri == "modificationDesc":
                results = results.order_by("-updated_at")
            else:
                results = results.order_by("-created_at")

        else:
            results = IPAddress.objects.all().order_by("-created_at")

    return render(
        request,
        "deepweb/index.html",
        {
            "form": form,
            "results": results,
            "reports": reports,
            "recent_reports": recent_reports,
        },
    )


def ip_chart_data(request, ip_address):
    """
    API endpoint for chart data.
    Returns JSON data for Chart.js with timeline, threat types, and users.
    """
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return JsonResponse({"error": "Adresse IP invalide"}, status=400)

    try:
        ip_obj = IPAddress.objects.get(address=ip_address)
    except IPAddress.DoesNotExist:
        return JsonResponse({"error": "IP non trouvée"}, status=404)

    reports = ip_obj.reports.select_related("user").order_by("created_at")

    if not reports.exists():
        return JsonResponse(
            {
                "timeline": {"labels": [], "data": []},
                "threatTypes": {"labels": [], "data": []},
                "topUsers": {"labels": [], "data": []},
            }
        )

    # Timeline data - group by day
    timeline_data = {}
    for report in reports:
        date_str = report.created_at.strftime("%Y-%m-%d")
        timeline_data[date_str] = timeline_data.get(date_str, 0) + 1

    # Sort by date
    sorted_dates = sorted(timeline_data.keys())
    timeline = {
        "labels": sorted_dates,
        "data": [timeline_data[date] for date in sorted_dates],
    }

    # Threat types distribution
    threat_counts = (
        reports.values("reason").annotate(count=Count("id")).order_by("-count")
    )
    threat_types = {
        "labels": [
            dict(Report.REASON_CHOICES).get(item["reason"], item["reason"])
            for item in threat_counts
        ],
        "data": [item["count"] for item in threat_counts],
    }

    # Top 5 users
    user_counts = (
        reports.values("user__username")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )
    top_users = {
        "labels": [item["user__username"] for item in user_counts],
        "data": [item["count"] for item in user_counts],
    }

    response_data = {
        "timeline": timeline,
        "threatTypes": threat_types,
        "topUsers": top_users,
    }

    return JsonResponse(response_data)


def statistics(request):
    """
    Display statistics page with charts and metrics.
    Shows reporting trends, top reported IPs, and geographic distribution.
    """
    now = timezone.now()

    # Calculate report counts for different time periods
    reports_last_hour = Report.objects.filter(
        created_at__gte=now - timedelta(hours=1)
    ).count()
    reports_last_24h = Report.objects.filter(
        created_at__gte=now - timedelta(hours=24)
    ).count()
    reports_last_7d = Report.objects.filter(
        created_at__gte=now - timedelta(days=7)
    ).count()
    reports_last_30d = Report.objects.filter(
        created_at__gte=now - timedelta(days=30)
    ).count()

    # Get top 10 most reported IPs in last 24 hours
    top_ips_24h = (
        Report.objects.filter(created_at__gte=now - timedelta(hours=24))
        .values("ip_address__address", "ip_address__hostname")
        .annotate(
            report_count=Count("id"),
            unique_users=Count("user", distinct=True),
        )
        .order_by("-report_count")[:10]
    )

    # Get recently reported IPs (last 20)
    recent_ips = (
        Report.objects.select_related("ip_address")
        .order_by("-created_at")
        .values_list("ip_address__address", flat=True)
        .distinct()[:20]
    )

    context = {
        "reports_last_hour": reports_last_hour,
        "reports_last_24h": reports_last_24h,
        "reports_last_7d": reports_last_7d,
        "reports_last_30d": reports_last_30d,
        "top_ips_24h": top_ips_24h,
        "recent_ips": recent_ips,
    }

    return render(request, "deepweb/statistics.html", context)


def statistics_chart_data(request, timeframe):
    """
    API endpoint for statistics chart data.
    Returns JSON data for Chart.js with different timeframes.
    Timeframes: 'day' (last 24 hours), 'week' (last 7 days), 'month' (last 30 days)
    """
    now = timezone.now()

    if timeframe == "day":
        # Last 24 hours, grouped by hour
        start_time = now - timedelta(hours=24)
        reports = (
            Report.objects.filter(created_at__gte=start_time)
            .annotate(hour=TruncHour("created_at"))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("hour")
        )

        labels = []
        data = []
        for report in reports:
            labels.append(report["hour"].strftime("%H:%M"))
            data.append(report["count"])

    elif timeframe == "week":
        # Last 7 days, grouped by day
        start_time = now - timedelta(days=7)
        reports = (
            Report.objects.filter(created_at__gte=start_time)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        labels = []
        data = []
        for report in reports:
            labels.append(report["day"].strftime("%Y-%m-%d"))
            data.append(report["count"])

    elif timeframe == "month":
        # Last 30 days, grouped by day
        start_time = now - timedelta(days=30)
        reports = (
            Report.objects.filter(created_at__gte=start_time)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        labels = []
        data = []
        for report in reports:
            labels.append(report["day"].strftime("%Y-%m-%d"))
            data.append(report["count"])

    else:
        return JsonResponse({"error": "Invalid timeframe"}, status=400)

    return JsonResponse({"labels": labels, "data": data})


def statistics_threat_data(request):
    """
    API endpoint for threat distribution chart.
    Returns threat types distribution for the last 7 days.
    """
    now = timezone.now()
    start_time = now - timedelta(days=7)

    threat_data = (
        Report.objects.filter(created_at__gte=start_time)
        .values("reason")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    labels = [
        dict(Report.REASON_CHOICES).get(item["reason"], item["reason"])
        for item in threat_data
    ]
    data = [item["count"] for item in threat_data]

    return JsonResponse({"labels": labels, "data": data})


def profile_public_user(request, pk):
    """Profile publique d'un utilisateur"""
    utilisateur = get_object_or_404(User, id=pk)
    reports = Report.objects.filter(user=utilisateur)

    return render(
        request,
        "deepweb/profile_public_user.html",
        {"utilisateur": utilisateur, "reports": reports},
    )


@login_required
def my_reports(request):
    """Report d'un utilisateur"""
    utilisateur = request.user
    reports = Report.objects.filter(user=utilisateur)

    if request.method == "POST":
        report_ids = request.POST.getlist("report_ids")

        if report_ids:
            Report.objects.filter(id__in=report_ids, user=utilisateur).delete()
            messages.success(
                request,
                f"{len(report_ids)} signalement(s) supprimé(s) avec succès",
            )
            return redirect("my_reports")

    return render(
        request,
        "deepweb/my_reports.html",
        {"utilisateur": utilisateur, "reports": reports},
    )


@login_required
def my_reports_delete(request, pk):
    """Supprimer son report"""
    report = get_object_or_404(Report, id=pk, user=request.user)

    if request.method == "POST":
        report.delete()
        messages.success(request, "Signalement supprimé")
        return redirect("my_reports")

    return render(request, "deepweb/my_reports_delete.html", {"report": report})


def mettre_a_jour_utilisateur(request, utilisateur):
    utilisateur.email = request.POST.get("email", utilisateur.email)
    utilisateur.first_name = request.POST.get("first_name", utilisateur.first_name)
    utilisateur.last_name = request.POST.get("last_name", utilisateur.last_name)
    password = request.POST.get("password")
    password_confirm = request.POST.get("password_confirm")
    if password and password_confirm:
        if password == password_confirm:
            utilisateur.set_password(password)
        else:
            utilisateur.password = utilisateur.password

    utilisateur.save()


def modifier_compte(request, id):
    """Modifier le profile utilisatreur"""
    utilisateur = request.user
    if not utilisateur.is_authenticated:
        messages.error(request, "Vous devez être connecté pour modifier votre profil.")
        return redirect("connecter")
    if utilisateur.id != id:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect("index")

    if request.method == "POST":
        form = UpdateProfileForm(request.POST, instance=utilisateur)
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        if form.is_valid():
            if password and password_confirm:
                if password == password_confirm:
                    mettre_a_jour_utilisateur(request, utilisateur)
                form.save()
                messages.success(request, "Profil mis à jour avec succès !")
                return redirect("modifier_compte", id=id)

            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return render(request, "deepweb/modifier_compte.html", {"form": form})

        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = UpdateProfileForm(instance=utilisateur)

    return render(request, "deepweb/modifier_compte.html", {"form": form})


def confirmer_suppression(request):
    """Confirmer la suppression d'un compte"""
    return render(request, "deepweb/confirmer_suppression.html")


def supprimer_compte(request, id):
    """Supprimer le compte"""
    utilisateur = request.user
    if not utilisateur.is_authenticated:
        messages.error(request, "Vous devez être connecté pour supprimer votre profil.")
        return redirect("modifier_compte", id=id)
    if utilisateur.id != id:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect("modifier_compte", id=id)
    if request.method == "POST":
        utilisateur.is_active = False
        utilisateur.save()
        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect("index")


def check_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        exists = User.objects.filter(email=email, is_active=True).exists()
        return JsonResponse({"exists": exists})
    return JsonResponse({"exists": False})
