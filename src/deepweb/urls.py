from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.register, name="signup"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.connecter, name="connecter"),
    path("accounts/logout/", views.deconnecter, name="deconnecter"),
    path("search/", views.rechercher, name="rechercher"),
    path("user/", views.list_user, name="list_user"),
    path("user/<int:pk>", views.list_user_update, name="list_user_update"),
    path(
        "profilepublic/user/<int:pk>",
        views.profile_public_user,
        name="profile_public_user",
    ),
    # IP and Report URLs
    path("check/<str:ip_address>/", views.ip_detail, name="ip_detail"),
    path("report/", views.report_ip, name="report_ip"),
    path("report/<str:ip_address>/", views.report_ip, name="report_ip"),
    # API endpoints
    path("api/chart/<str:ip_address>/", views.ip_chart_data, name="ip_chart_data"),
    path("api/reports/<str:ip_address>/", views.ip_reports_api, name="ip_reports_api"),
]
