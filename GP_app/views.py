from django.shortcuts import render
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@login_required
@allowed_users(allowed_roles=['normal_user'])
def index(request):
    return render(request, 'base.html' )
@login_required
@allowed_users(allowed_roles=['normal_user'])
def home(request):
    return render(request, 'layout/dashboard.html' )

# def analytics_view(request):
#     return render(request, 'layout/analytics.html' )
@login_required
@allowed_users(allowed_roles=['normal_user'])
def reports_view(request):
    return render(request, 'layout/reports.html' )
@unauthenticated_user
def welcome_view(request):
    return render(request, 'welcome.html' )
@unauthenticated_user
def the_welcome(request):
    return render(request, 'theWelocm.html')
