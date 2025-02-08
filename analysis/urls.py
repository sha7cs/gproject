from django.urls import path
from . import views

urlpatterns = [
    path('filter-data/', views.filter_data, name='filter_data'),
    path('', views.analysis_view, name='analysis'),
    #path('/analysis/', views.analysis_view, name='analysis'),
]

