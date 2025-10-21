from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.register, name="signup"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.connecter, name="connecter"),
    path("accounts/logout/", views.deconnecter, name="deconnecter"),
    path("search/", views.rechercher, name="rechercher"),
<<<<<<< HEAD
=======
    path("user/", views.list_user, name="list_user"),
    path("user/<int:pk>", views.list_user_update, name="list_user_update"),
>>>>>>> 1e90755596fdc22bc4c3a5332fc6fd4e842f15bc
    # IP and Report URLs
    path("check/<str:ip_address>/", views.ip_detail, name="ip_detail"),
    path("report/", views.report_ip, name="report_ip"),
    path("report/<str:ip_address>/", views.report_ip, name="report_ip"),
]
