from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
import logging
from .forms import CreateUser, UserProfileForm #هذولي الفورمز الي بنستخدمهم تلقونهم بفايل فورمز
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.models import Group 
from .decorators import allowed_users, admin_only, unauthenticated_user #هذولي الديكوريترز الي حنا مسوينهم نقدر نسوي الي نحتاج براحتنا
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from authentication_app.models import UserProfile ,City,Area


##واضح هذا حق الساين ان هههههههههه
@method_decorator(unauthenticated_user, name='dispatch')
class SignUpView(CreateView):
    template_name = 'authentication_app/signup_page.html'
    form_class = CreateUser # هذي الفروم الي يسويه ياخذه من الفرومز روحوا للملف فيه الشرح 
    success_url = reverse_lazy('user_settings')  # Redirect to home after signup او ممكن نخليه يروح للوق ان او السيتنقز بكيفنا

    def form_valid(self, form):
        user = form.save()
        ## هنا اي يوزر جديد يحطه بقروب النورمال يوزر 
        NormalUser_group, created = Group.objects.get_or_create(name='normal_user')  
        user.groups.add(NormalUser_group)
        
        #هذا البارت هو الي عليه اختلاف يا يسجله دخول على طول يا يقول له انت سجل من جديد 
        login(self.request, user) 
        messages.success(self.request, 'Account created successfully! You are now logged in.') 
        return redirect(self.success_url)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)


logger = logging.getLogger(__name__) ## هذا اتوقع يسجل اللقوز عشان نراقب الوضع ههههههههه
@method_decorator(unauthenticated_user, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'authentication_app/login_page.html'

    def get_success_url(self):
        user = self.request.user
        user_profile = getattr(user, 'userprofile', None)
        
        if user.is_staff:
            return reverse_lazy('admindashboard')

        if user_profile:  
            if user_profile.status == 0 and not user_profile.cafe_name or not user_profile.area:  # If either field is missing
                return reverse_lazy('user_settings')  # Force settings page
            elif user_profile.status == 0 and user_profile.cafe_name:
                # messages.warning()
                return reverse_lazy('wait')
            elif user_profile.status == 2:
                messages.error(self.request, "Your account has been denied. Contact support.")
                return reverse_lazy('login')  # Redirect back to login
            return reverse_lazy('home')  # Approved users go to home
        
        # If for some reason the user has no UserProfile, log them out
        messages.error(self.request, "No profile associated with this account.")
        return reverse_lazy('login')
    
    
    def form_valid(self, form):
        logger.info(f"User {form.get_user().username} logged in.")
        messages.success(self.request,f"مرحبًا بك يا {form.get_user().username}")
        return super().form_valid(form)

    def form_invalid(self, form):
 
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")

        return super().form_invalid(form)
    # هذي لاي شيء نبغى نضيفه زياده ينرسل 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_message'] = 'Log in to access your dashboard.'
        return context
 
 
##هنا كل هذولي سويتهم بش عشان اضبط الزيدايركت والا يبيلهم شغل واشياء 
@login_required
@allowed_users(allowed_roles=['admins','normal_user'])
def settings(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.cafe_name and user_profile.area:  # نشوف لو هم الريدي عبوا السيتينقز قبل وللحين ماقبلناهم ما يدخلهم
            messages.info(request, "You have already submitted your profile. You cannot access the settings page.")
            return redirect('wait')  

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user 
            user_profile.save()

            messages.success(request,'submitted')
            return redirect("wait") 
        else:
            # If form is invalid, we still want to render the form with error messages
            areas = Area.objects.all()
            cities = City.objects.all()  
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            return render(request, 'profile/profile-settings.html', {'form': form, 'areas': areas, 'cities': cities})
    else:
        areas = Area.objects.all()
        cities = City.objects.all()
        form = UserProfileForm()
        return render(request, 'profile/profile-settings.html', {'form': form, 'areas': areas, 'cities': cities})
    
@login_required
@admin_only
def admindashboard(request):
    return redirect('admins.users')

#هذي كتبه لي جبت يبي له تعديل مسميات وتعتمد على المودل الي بنسويه بس فمرته تعديل البيانات عادي
@login_required
@allowed_users(allowed_roles=['normal_user'])
def update_settings(request):
    user_profile = request.user.userprofile  
    form = UserProfileForm(instance=user_profile)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_settings')

    return render(request, 'settings_update.html', {'form': form})


def waiting(request):
    return render(request, 'profile/waiting.html')