from . import views
from django.urls import path, include
from .views import CustomLoginView, SignUpView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # path('set-lang/<str:urlname>/', views.set_language, name='set_language'),
    path('signup', SignUpView.as_view(), name='signup'),
    path('login' , CustomLoginView.as_view() , name='login'),
    path('logout/', LogoutView.as_view(next_page='theWelcome'), name='logout'),
    path('settings', views.settings, name = "user_settings"),
    path('update-settings/', views.update_settings, name='update_settings'),
    path('admindashboard/', views.admindashboard, name = "admindashboard"),
    path('waiting/', views.waiting, name = "wait"),
    path('mysettings/',views.settings_view, name="settings_view"),
    path('mysettings/update',views.settings_update, name="settings_update"),
    path('mysettings/events/', views.user_events_view, name='user_events_view'),
]  