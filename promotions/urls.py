from . import views
from django.urls import path, include
from .views import promotions_page  


urlpatterns = [
    # path('' , views.promotions_view , name='promotions'),
    path('set-lang/<str:urlname>/', views.set_language, name='set_language'),
    path('' , views.chatbot , name='promotions'),
    path('promotions/', views.promotions_page, name='promotions'),
]