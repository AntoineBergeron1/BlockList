import os
from .models import User, IPAddress, Report
from .forms import RegisterForm, LoginForm, ReportForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Count, Min, Max

utilisateurs = User.objects.all()

# Create your views here.


def index(request):
    return render(request, "deepweb/index.html")

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

    return render(request, "deepweb/login.html", {"form": form})


def deconnecter(request):
    logout(request)
    messages.success(request, "Déconnecté avec succès !")
    return redirect("index")


def ip_detail(request, ip_id):
    """
    Display IP address details with reports history.
    Shows first 10 reports, with AJAX load more functionality.
    """
    ip_address = get_object_or_404(IPAddress, pk=ip_id)

    # Get reports with statistics
    reports = ip_address.reports.select_related("user").order_by("-created_at")

    # Calculate statistics
    total_reports = reports.count()
    first_report_date = reports.aggregate(Min("created_at"))["created_at__min"]
    last_report_date = reports.aggregate(Max("created_at"))["created_at__max"]

    # Get first 10 reports for initial load
    initial_reports = reports[:10]

    context = {
        "ip_address": ip_address,
        "reports": initial_reports,
        "total_reports": total_reports,
        "first_report_date": first_report_date,
        "last_report_date": last_report_date,
        "has_more": total_reports > 10,
    }

    return render(request, "deepweb/ip_detail.html", context)


@login_required
def report_ip(request, ip_id=None):
    """
    Form to report an IP address.
    If ip_id is provided, pre-fill the IP address (readonly).
    """
    ip_address = None
    if ip_id:
        ip_address = get_object_or_404(IPAddress, pk=ip_id)

    if request.method == "POST":
        form = ReportForm(request.POST, ip_address=ip_address)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()

            messages.success(
                request,
                f"Signalement enregistré avec succès pour l'IP {report.ip_address.address}!"
            )
            return redirect("ip_detail", ip_id=report.ip_address.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ReportForm(ip_address=ip_address)

    context = {
        "form": form,
        "ip_address": ip_address,
    }

    return render(request, "deepweb/report_form.html", context)
