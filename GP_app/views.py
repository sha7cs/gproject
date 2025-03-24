from django.shortcuts import render
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user,approved_user_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@login_required
@allowed_users(allowed_roles=['admins','normal_user'])
@approved_user_required
def index(request):
    return render(request, 'base.html' )

@login_required
@allowed_users(allowed_roles=['admins','normal_user'])
@approved_user_required
def home(request):
    return render(request, 'layout/dashboard.html' )

# def analytics_view(request):
#     return render(request, 'layout/analytics.html' )
@login_required
@allowed_users(allowed_roles=['normal_user','admins'])
@approved_user_required
def reports_view(request):
    return render(request, 'layout/reports.html' )

def welcome_view(request):
    return render(request, 'welcome.html' )