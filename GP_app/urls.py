from django.urls import path, include
from . import views


urlpatterns = [
    # path('index/' , views.index , name='home'),
    path('home/' , views.home , name='home'),
    # path('analytics/' , views.analytics_view , name='analytics'),
    path('reports/' , views.reports_view , name='reports'),
    path('' , views.welcome_view ,  name='theWelcome'),
    # path('chatbot/', include('chatbot.urls'))
]