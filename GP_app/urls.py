from django.urls import path
from . import views


urlpatterns = [
    # path('index/' , views.index , name='home'),
    path('home/' , views.home , name='home'),
    path('analytics/' , views.analytics_view , name='analytics'),
    path('promotions/' , views.promotions_view , name='promotions'),
    path('reports/' , views.reports_view , name='reports'),
]