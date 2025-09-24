from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, "deepweb/index.html")

def register(request):
    return render(request, "registration/register.html")


def connecter(request):
    return render(request, "/registration/login.html")
