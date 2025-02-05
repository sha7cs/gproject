from django.shortcuts import render


def index(request):
    return render(request, 'base.html' )

def home(request):
    return render(request, 'layout/dashboard.html' )

def analytics_view(request):
    return render(request, 'layout/analytics.html' )

def reports_view(request):
    return render(request, 'layout/reports.html' )

def welcome_view(request):
    return render(request, 'welcome.html' )
