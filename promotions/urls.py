from . import views
from django.urls import path, include
from . import views


urlpatterns = [
    # path('' , views.promotions_view , name='promotions'),
    path('set-lang/<str:urlname>/', views.set_language, name='set_language'),
    path('' , views.chatbot , name='promotions'),
    path('reset-chat', views.delete_thread,name='delete_thread')
]