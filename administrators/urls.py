from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name="admins.base"),
    path('users/', views.users , name="admins.users"),
    path('accept-user/<int:user_id>/', views.accept_user, name='accept_user'),
]