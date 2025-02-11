from . import views
from django.urls import path, include

urlpatterns = [
    # path('set-lang/<str:urlname>/', views.set_language, name='set_language'),
    path('signup' , views.signup , name='signup'),
    path('login' , views.login_page , name='login_page'),
]  