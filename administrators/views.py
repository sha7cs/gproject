from django.shortcuts import render
from authentication_app.models import UserProfile 

def index(request):
    return render(request, 'admins/base.html')


def users(request):
    profiles = UserProfile.objects.select_related('user').all()

    # Define status classes and Arabic translation
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

    # Assign Arabic translation and class
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
    
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

def accept_user(request, user_id):
    profile = get_object_or_404(UserProfile, id=user_id)
    
    # Update the status to Accepted
    profile.status = UserProfile.ACCEPTED
    profile.save()

    messages.success(request, f"{profile.user.username} has been accepted.")
    return redirect('admins.users')  