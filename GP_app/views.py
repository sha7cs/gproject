from django.shortcuts import render
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user,approved_user_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from analysis.views import get_sales_data
from authentication_app.models import UserProfile
from promotions.views import marketing_advice, get_next_event
@login_required
@allowed_users(allowed_roles=['admins','normal_user'])
@approved_user_required
def index(request):
    return render(request, 'base.html' )

@login_required
@allowed_users(allowed_roles=['admins','normal_user'])
@approved_user_required
def home(request):
    profile = UserProfile.objects.get(user=request.user)  # Get the user's profile
    df = get_sales_data(profile)  # Get the sales data

    detailed_orders = df['detailed_orders'].dropna()
    category_sales = {}
    for order in detailed_orders:
        for item in order:
            category_sales[item['category']] = category_sales.get(item['category'], 0) + item['quantity']
    advice_title, advice_text = marketing_advice()
    next_event = get_next_event()
    context = {
        'username': profile.cafe_name,
        'category_labels': list(category_sales.keys()),
        'category_data': list(category_sales.values()),
        'advice_title' : advice_title,
        'next_event': next_event
    }
    return render(request, 'layout/dashboard.html', context)


@login_required
@allowed_users(allowed_roles=['normal_user','admins'])
@approved_user_required
def reports_view(request):
    return render(request, 'layout/reports.html' )

def welcome_view(request):
    return render(request, 'welcome.html' )

