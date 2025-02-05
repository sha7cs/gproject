from . import views
from django.urls import path, include

urlpatterns = [
    # path('' , views.promotions_view , name='promotions'),
    path('/set-lang/', views.set_language, name='set_language'),
    path('' , views.chatbot , name='promotions'),
]