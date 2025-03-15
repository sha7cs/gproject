from django.shortcuts import render
from authentication_app.models import UserProfile 
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user #هذولي الديكوريترز الي حنا مسوينهم نقدر نسوي الي نحتاج براحتنا
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404


def index(request):
    return render(request, 'admins/base.html')

@login_required
@allowed_users(allowed_roles=['admins'])
def users(request):
    profiles_list = UserProfile.objects.select_related('user').all().order_by('-user__date_joined')

    # for the UI
    status_data = {
        UserProfile.PENDING: {
            "class": "badge badge-warning fas fa-clock",
            "text": "قيد الانتظار",
        },
        UserProfile.ACCEPTED: {
            "class": "badge badge-success fas fa-check-circle",
            "text": "مقبول",
        },
        UserProfile.DENIED: {
            "class": "badge badge-danger fas fa-times-circle",
            "text": "مرفوض",
        }
    }
    # filter by status
    status_filter = request.GET.get('status')  # Get status from URL
    if status_filter:
        profiles_list = profiles_list.filter(status=status_filter)

    # filter by date
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            profiles_list = profiles_list.filter(user__date_joined__range=[start_date, end_date])
        except ValueError:
            pass  # Ignore invalid dates

    # Pagination setup
    page = request.GET.get('page', 1)  # Get the current page number from the request
    paginator = Paginator(profiles_list, 10)  # 10 profiles per page
    profiles = paginator.get_page(page)  # Get the requested page

    # Assign status class and text
    for profile in profiles:
        profile.status_class = status_data[profile.status]["class"]
        profile.status_text = status_data[profile.status]["text"]

    # Count users by status
    pending_count = UserProfile.objects.filter(status=UserProfile.PENDING).count()
    accepted_count = UserProfile.objects.filter(status=UserProfile.ACCEPTED).count()
    denied_count = UserProfile.objects.filter(status=UserProfile.DENIED).count()
    total_count = UserProfile.objects.count()
    
    return render(request, 'admins/users.html', {
        'profiles': profiles,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'denied_count': denied_count,
        'total_count': total_count
    })
# what is left: 
# search by user name 
# show or filter by status 
# make the admin can see the details of the user request   
# اخليه ينرسل ايميل اذا قبلهم الادمن 
# ممكن نخلي المرفوضين بعد ما يمر عليهم عشر ايام نحذفهم من الداتا بيس
      
@login_required
@allowed_users(allowed_roles=['admins'])
def accept_user(request, user_id):
    profile = get_object_or_404(UserProfile, id=user_id)
    
    # Update the status to Accepted
    profile.status = UserProfile.ACCEPTED
    profile.save()

    messages.success(request, f"{profile.user.username} has been accepted.")
    return redirect('admins.users')  