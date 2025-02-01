from django.urls import path
from . import views

urlpatterns =[
 path('/set-lang/', views.set_language, name='set_language'),
 path('' , views.chatbot , name='chatbot'),
]