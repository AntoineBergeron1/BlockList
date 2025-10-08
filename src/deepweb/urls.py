from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.register, name="signup"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.connecter, name="connecter"),
    path("accounts/logout/", views.deconnecter, name="deconnecter"),
    path("search/", views.rechercher, name="rechercher"),
    # IP and Report URLs
    path("check/<str:ip_address>/", views.ip_detail, name="ip_detail"),
    path("report/", views.report_ip, name="report_ip"),
    path("report/<str:ip_address>/", views.report_ip, name="report_ip"),
]
