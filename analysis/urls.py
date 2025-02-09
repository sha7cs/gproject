from django.urls import path
from . import views

urlpatterns = [
    # path('set-lang/', views.set_language, name='set_language'),
    path('filter-data/', views.filter_data, name='filter_data'),
    path('', views.analysis_view, name='analysis'),
    #path('/analysis/', views.analysis_view, name='analysis'),
]

