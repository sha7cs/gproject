from django.shortcuts import render
from authentication_app.models import UserProfile 
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user #هذولي الديكوريترز الي حنا مسوينهم نقدر نسوي الي نحتاج براحتنا
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q 
from django.utils.translation import gettext_lazy as _  

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
            "text": _('Pending'),
        },
        UserProfile.ACCEPTED: {
            "class": "badge badge-success fas fa-check-circle",
            "text": _('Accepted'),
        },
        UserProfile.DENIED: {
            "class": "badge badge-danger fas fa-times-circle",
            "text": _('Denied'),
        }
    }
    
    # Search 
    search_query = request.GET.get('q', '').strip()
    if search_query:
        profiles_list = profiles_list.filter(
            Q(user__username__icontains=search_query) |
            Q(cafe_name__icontains=search_query)  |
            Q(id__icontains=search_query)
        )  # Modify as needed

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
        'total_count': total_count,
        'query': search_query,
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

    messages.success(request,_(f"{profile.user.username} has been accepted."))
    return redirect('admins.users')  

@login_required
@allowed_users(allowed_roles=['admins'])
def remove_user(request, user_id):
    profile = get_object_or_404(UserProfile, id=user_id)
    
    # Update the status to Accepted
    profile.status = UserProfile.DENIED
    profile.save()

    messages.success(request, _(f"{profile.user.username} has been Denied."))
    return redirect('admins.users')  


@login_required
@allowed_users(allowed_roles=['admins'])
def user_details(request, user_id):
    # Retrieve the user profile by ID
    user_profile = get_object_or_404(UserProfile, id=user_id)
    
    return render(request, 'admins/user_details.html', {'user_profile': user_profile})

# @login_required
# @allowed_users(allowed_roles=['admins'])
# def search_user(request):
#     query = request.GET.get('q', '')  # Get the search query
#     profiles_list = UserProfile.objects.select_related('user').all().order_by('-user__date_joined')
#     users = User.objects.none()  # Default empty queryset

#     if query:
#         users = User.objects.filter(username__icontains=query)  # Adjust filtering as needed

#     return render(request, 'users.html', {'profiles': users, 'query': query})