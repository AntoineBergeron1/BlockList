from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.register, name='signup'),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.connecter, name="connecter"),
    path('accounts/logout/', views.deconnecter, name='deconnecter'),

]
