from django.urls import path
from .views import analysis_view,filter_data 

urlpatterns = [
    path('', analysis_view, name='analysis_view'),  
    path('filter-data/', filter_data, name='filter_data'),
]
