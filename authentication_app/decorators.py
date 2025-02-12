from django.http import HttpResponse
from django.shortcuts import redirect
## هذا ملف الديكوريترز الي هي تحدد صلاحيات الوصول للاشياء او الفيوز، كل الموجود باختيارنا يعني حنا نقرر لو نبي جديده بشروط معينه كبفنا
## لو تمرون على الفيوز بتلقون فوق كل فيو اللي يحتاجه 



def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.exists():
                user_group = request.user.groups.all()[0].name
                if user_group in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('home')  # Redirect unauthorized users to home
            return redirect('login_page')  # Redirect non-logged-in users to login
        return wrapper_func
    return decorator

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_superuser:  # Check if user is a superuser (admin)
            return view_func(request, *args, **kwargs)
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

