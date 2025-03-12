from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages

## هذا ملف الديكوريترز الي هي تحدد صلاحيات الوصول للاشياء او الفيوز، كل الموجود باختيارنا يعني حنا نقرر لو نبي جديده بشروط معينه كبفنا
## لو تمرون على الفيوز بتلقون فوق كل فيو اللي يحتاجه 

# admins , normal_user

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            user_profile = getattr(request.user, 'userprofile', None) 
            if request.user.groups.exists():
                user_group = request.user.groups.all()[0].name
                if user_group in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    if request.user.is_staff or request.user.is_superuser:
                            return redirect('admindashboard')
                    elif not user_profile or user_profile.status != 1:
                        messages.error(request, "حسابك لا زال قيد الانتظار، لا يمكنك دخول هذه الصفحة.")
                        return redirect('user_settings')  # Redirect to settings page
                    return redirect('home')  # Redirect unauthorized users to home
            return redirect('login_page')  # Redirect non-logged-in users to login
        return wrapper_func
    return decorator

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        user_profile = getattr(request.user, 'userprofile', None)
        if request.user.is_superuser:  # Check if user is a superuser (admin)
            return view_func(request, *args, **kwargs)
        elif not user_profile or user_profile.status != 1:
            messages.error(request, "حسابك لا زال غير مصرح له الدخول.")
            return redirect('user_settings')  # Redirect to settings page
        return redirect('home')  # Redirect normal users to home
    return wrapper_func


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return redirect('admindashboard')  # Redirect staff/admin users to admin dashboard
            return redirect('home')  # Redirect normal users to home
        return view_func(request, *args, **kwargs)
    return wrapper_func


from functools import wraps
def approved_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_profile = getattr(request.user, 'userprofile', None)  # Get UserProfile safely

        if not user_profile or user_profile.status != 1:  # Not approved
            messages.error(request, "حسابك لا زال قيد الانتظار، لا يمكنك دخول هذه الصفحة.")
            return redirect('user_settings')  # Redirect to settings page
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view