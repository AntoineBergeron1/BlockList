import os
from .models import User
from .forms import (RegisterForm, LoginForm)
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.core.files.storage import FileSystemStorage

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
