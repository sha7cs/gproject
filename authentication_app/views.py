from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
import logging
from .forms import CreateUser, UserProfileForm, UserUpdateForm
from django.contrib import messages
from django.urls import reverse_lazy,reverse
from django.views.generic.edit import CreateView,UpdateView
from django.contrib.auth.models import Group 
from .decorators import allowed_users, admin_only, unauthenticated_user #هذولي الديكوريترز الي حنا مسوينهم نقدر نسوي الي نحتاج براحتنا
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from authentication_app.models import UserProfile ,City,Area
from django.utils.translation import gettext_lazy as _ 
from django.http import HttpResponseRedirect
from promotions.models import Event
from promotions.forms import EventForm
from django.db.models import Q
from django.utils.translation import get_language, gettext_lazy as _
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.shortcuts import get_object_or_404

@login_required
def user_events_view(request):
    user_profile = request.user.userprofile

    user_events = Event.objects.filter(user=user_profile)
    admin_events = Event.objects.filter(user__isnull=True)

    if request.method == 'POST':
        action = request.POST.get('action')
        event_id = request.POST.get('event_id')

        if action == 'delete' and event_id:
            Event.objects.filter(id=event_id, user=user_profile).delete()
            messages.success(request, _("Event deleted successfully."))
            return HttpResponseRedirect(reverse('settings_view') + '#events')

        elif action == 'edit' and event_id:
            try:
                event = Event.objects.get(id=event_id, user=user_profile)
                event.date = request.POST.get('date')

                event.set_current_language('en')
                event.name = request.POST.get('name_en')
                event.description = request.POST.get('description')
                event.save()

                event.set_current_language('ar')
                event.name = request.POST.get('name_ar')
                event.save()

                messages.success(request, _("Event updated successfully."))
            except Event.DoesNotExist:
                messages.error(request, _("Event not found."))

            return HttpResponseRedirect(reverse('settings_view') + '#events')

        elif action == 'add':
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.user = user_profile  
                event.save()

                event.set_current_language('en')
                event.name = form.cleaned_data['name_en']
                event.description = form.cleaned_data['description']
                event.save()

                event.set_current_language('ar')
                event.name = form.cleaned_data['name_ar']
                event.save()

                messages.success(request, _("Event added successfully."))
                return HttpResponseRedirect(reverse('settings_view') + '#events')

    else:
        form = EventForm()

    return render(request, 'profile/settings_view.html', {
        'form_event': form,
        'events': user_events,
        'admin_events': admin_events
    })


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
        messages.success(self.request, _('Account created successfully! You are now logged in.')) 
        return redirect(self.success_url)

    # def form_invalid(self, form):
    #     for field, errors in form.errors.items():
    #         for error in errors:
    #             messages.error(self.request, _(f"{field.capitalize()}: {error}"))
    #     return super().form_invalid(form)


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
                messages.error(self.request, _("Your account has been denied. Contact support."))
                return reverse_lazy('login')  # Redirect back to login
            return reverse_lazy('home')  # Approved users go to home
        
        # If for some reason the user has no UserProfile, log them out
        messages.error(self.request, _("No profile associated with this account."))
        return reverse_lazy('login')
    
    
    def form_valid(self, form):
        logger.info(f"User {form.get_user().username} logged in.")
        messages.success(self.request,_(f"Welcome back, {form.get_user().username}"))
        return super().form_valid(form)

    # def form_invalid(self, form):
 
    #     for field, errors in form.errors.items():
    #         for error in errors:
    #             messages.error(self.request, f"{field.capitalize()}: {error}")

        return super().form_invalid(form)
    # هذي لاي شيء نبغى نضيفه زياده ينرسل 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_message'] = 'Log in to access your dashboard.'
        return context

@login_required
@allowed_users(allowed_roles=['admins','normal_user'])
def settings(request):
    try:
        # اذا كان ما عبى السيتينقز بيطلع هنا ايرور عشان كذا فيه تراي وكاتش
        user_profile = UserProfile.objects.get(user=request.user)

        # اذا كد عبوا السيتينقز ما يسمح لهم يدخلونها ويوديهم صفحة الانتظار
        if user_profile.cafe_name and user_profile.area:
            messages.info(request, _("You have already submitted your profile. You cannot access the settings page."))
            return redirect('wait')

    except UserProfile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user 
            user_profile.save()
            #send email
            html_message = render_to_string('admins/pending_email.html', {'cafe_name': user_profile.cafe_name})
            send_mail(
                'قيد الانتظار - منصة عد',
                '',
                django_settings.EMAIL_HOST_USER,
                [user_profile.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            messages.success(request, _('Your request has been submitted.'))
            return redirect("wait") 
        else:
            # If form is invalid, we still want to render the form with error messages
            areas = Area.objects.all()
            cities = City.objects.all()  
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _(f"{field.capitalize()}: {error}"))
            return render(request, 'profile/signup-settings.html', {'form': form, 'areas': areas, 'cities': cities})
    else:
        areas = Area.objects.all()
        cities = City.objects.all()
        form = UserProfileForm()
        return render(request, 'profile/signup-settings.html', {'form': form, 'areas': areas, 'cities': cities})
    
@login_required
@admin_only
def admindashboard(request):
    return redirect('admins.users')

def waiting(request):
    return render(request, 'profile/waiting.html')


@login_required
@allowed_users(allowed_roles=['admins', 'normal_user'])
def settings_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    areas = Area.objects.all()
    cities = City.objects.all()

    form = UserProfileForm(instance=user_profile)    
    user_form = UserUpdateForm(instance=request.user)

    form_event = EventForm()
    user_events = Event.objects.filter(user=user_profile) # user event
    admin_events = Event.objects.filter(user__isnull=True)  # admin event
    

    return render(request, 'profile/settings_view.html', {
        'user': user_profile,
        'areas': areas,
        'cities': cities,
        'form': form,
        'user_form': user_form,
        'form_event': form_event,
        'events': user_events,  
        'admin_events': admin_events,
    })


@login_required
@allowed_users(allowed_roles=['admins','normal_user'])
def settings_update(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        user_form= UserUpdateForm(request.POST,instance= request.user)
        
        if form.is_valid() and user_form.is_valid():
            form.save()
            user_form.save()
            messages.success(request, _("Profile updated successfully!"))
            return redirect('settings_view')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _(f"{field.capitalize()}: {error}"))
                    print('')
            return redirect('settings_view')
