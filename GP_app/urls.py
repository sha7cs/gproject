from django.urls import path, include
from . import views


urlpatterns = [
    path('home/' , views.home , name='home'),
    path('reports/' , views.reports_view , name='reports'),
    path('' , views.welcome_view ,  name='theWelcome'),
]