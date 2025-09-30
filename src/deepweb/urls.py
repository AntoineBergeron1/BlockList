from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.register, name='signup'),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.connecter, name="connecter"),
    path('accounts/logout/', views.deconnecter, name='deconnecter'),

    # IP and Report URLs
    path('ip/<int:ip_id>/', views.ip_detail, name='ip_detail'),
    path('report/', views.report_ip, name='report_ip'),
    path('report/<int:ip_id>/', views.report_ip, name='report_ip'),
]
