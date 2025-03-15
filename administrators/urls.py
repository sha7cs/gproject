from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name="admins.base"),
    path('users/', views.users , name="admins.users"),
    path('user/<int:user_id>/', views.user_details, name='user_details'),
    path('accept-user/<int:user_id>/', views.accept_user, name='accept_user'),
    path('remove_user/<int:user_id>/', views.remove_user, name='remove_user'),

]