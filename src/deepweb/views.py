import ipaddress
import os

from django.conf import (  # TODO: Used for DEBUG in login view quick-login buttons
    settings,
)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Count, Max, Min
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, RegisterForm, ReportForm, SearchForm
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
            "results": IPAddress.objects.all(),
            "reports": reports,
            "recent_reports": recent_reports,
        },
    )


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
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

    # TODO: Remove 'debug' context when removing quick-login development buttons
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
            resultat_recherche = form.cleaned_data["recherche"]
            optiontri = form.cleaned_data.get("tries")
            if resultat_recherche:
                results = []
                for ip in IPAddress.objects.all():
                    if resultat_recherche in ip.address:
                        results.append(ip)
            else:
                results = IPAddress.objects.all()

            if optiontri == "reputationCroissant":
                results = results.order_by("-reputation_score")
            elif optiontri == "reputationDecroissant":
                results = results.order_by("reputation_score")
            elif optiontri == "creationCroissant":
                results = results.order_by("created_at")
            elif optiontri == "creationDecroissant":
                results = results.order_by("-created_at")
            elif optiontri == "modificationCroissant":
                results = results.order_by("updated_at")
            elif optiontri == "modificationDecroissant":
                results = results.order_by("-updated_at")
            elif optiontri == "default":
                results = results

            else:
                results = IPAddress.objects.none()

        else:
            results = IPAddress.objects.all()

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
