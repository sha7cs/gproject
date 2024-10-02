from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'base.html' )


def home(request):
    return render(request, 'layout/dashboard.html' )

def analytics_view(request):
    return render(request, 'layout/analytics.html' )

def promotions_view(request):
    return render(request, 'layout/promotions.html' )

def reports_view(request):
    return render(request, 'layout/reports.html' )
