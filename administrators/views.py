from django.shortcuts import render
from authentication_app.models import UserProfile 
from promotions.models import Category,Subcategory,Question,Event
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user #هذولي الديكوريترز الي حنا مسوينهم نقدر نسوي الي نحتاج براحتنا
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q 
from django.utils.translation import gettext_lazy as _  
from django.core.mail import send_mail
from django.conf import settings
from django.db import models  

@login_required
@allowed_users(allowed_roles=['admins'])
def event_control(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id)
            event.delete()
            messages.success(request, _("Event deleted successfully."))

        elif action == 'edit':
            event_id = request.POST.get('event_id')
            name_ar = request.POST.get('name_ar')
            name_en = request.POST.get('name_en')
            description = request.POST.get('description', '')
            date = request.POST.get('date')

            event = get_object_or_404(Event, id=event_id)
            event.date = date

            event.set_current_language('ar')
            event.name = name_ar
            event.description = description
            event.save()

            event.set_current_language('en')
            event.name = name_en
            event.save()

            messages.success(request, _("Event updated successfully."))

        else:  # default: add single event for all
            name_ar = request.POST.get('name_ar')
            name_en = request.POST.get('name_en')
            description = request.POST.get('description', '')
            date = request.POST.get('date')

            try:
                event = Event.objects.create(date=date)
                event.set_current_language('ar')
                event.name = name_ar
                event.description = description
                event.save()

                event.set_current_language('en')
                event.name = name_en
                event.save()

                messages.success(request, _("Event added successfully!"))
            except Exception as e:
                messages.error(request, _(f"Error: {e}"))

        return redirect("admins.events")

    # GET
    events = Event.objects.filter(user__isnull=True).order_by('-date')  # only global events
    return render(request, "admins/event_control.html", {
        "events": events
    })






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

from django.template.loader import render_to_string
    
@login_required
@allowed_users(allowed_roles=['admins'])
def accept_user(request, user_id):
    profile = get_object_or_404(UserProfile, id=user_id)
    
    # Update the status to Accepted
    profile.status = UserProfile.ACCEPTED
    profile.save()
    
    
    html_message = render_to_string('admins/acceptance_email.html', {'cafe_name': profile.cafe_name})
    send_mail(
        '☕️ تم قبولك في منصة عد!',
        '',
        settings.EMAIL_HOST_USER,
        [profile.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    messages.success(request,_(f"{profile.user.username} has been accepted."))
    return redirect('admins.users')  

@login_required
@allowed_users(allowed_roles=['admins'])
def remove_user(request, user_id):
    profile = get_object_or_404(UserProfile, id=user_id)
    
    # Update the status to Accepted
    profile.status = UserProfile.DENIED
    profile.save()
    #send email
    html_message = render_to_string('admins/reject_email.html', {'cafe_name': profile.cafe_name})
    send_mail(
        'نعتذر منك - منصة عد',
        '',
        settings.EMAIL_HOST_USER,
        [profile.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    messages.success(request, _(f"{profile.user.username} has been Denied."))
    return redirect('admins.users')  


@login_required
@allowed_users(allowed_roles=['admins'])
def user_details(request, user_id):
    # Retrieve the user profile by ID
    user_profile = get_object_or_404(UserProfile, id=user_id)
    
    return render(request, 'admins/user_details.html', {'user_profile': user_profile})



from .forms import QuestionForm , SubcategoryForm

@login_required
@allowed_users(allowed_roles=['admins'])
def chat_control(request):
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    allquestions = Question.objects.all()

    if request.method == "POST":
        for question in allquestions:
            question_id = request.POST.get(f"question_id_{question.id}") 
            
            if question_id:
                question = get_object_or_404(Question, id=question_id)
                question_ar = request.POST.get(f"question_ar_{question.id}")
                question_en = request.POST.get(f"question_en_{question.id}")

                if question_ar:
                    question.set_current_language('ar') 
                    question.question = question_ar  # Update the Arabic translation
                    question.save()

                if question_en:
                    question.set_current_language('en') 
                    question.question = question_en  # Update the English translation
                    question.save()

        messages.success(request, _("Questions updated successfully!"))
        return redirect("admins.chatbot")  
    formQ = QuestionForm()
    form_subcategory = SubcategoryForm()
    return render(request, "admins/chat_control.html", {
        "categories": categories,
        "subcategories": subcategories,
        "questions": allquestions,
        'formQ': formQ,
        'form_subcategory':form_subcategory,
    })


@login_required
@allowed_users(allowed_roles=['admins'])
def create_question(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.subcategory = subcategory 
            new_question.save()
            messages.success(request, _("New question created successfully!"))
            return redirect('admins.chatbot') 
        else:
            messages.error(request, _("There was an error creating the question."))
            return redirect('admins.chatbot') 
            

@login_required
@allowed_users(allowed_roles=['admins'])
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    question.delete()

    messages.success(request, _("Question deleted successfully!"))
    return redirect('admins.chatbot')

@login_required
@allowed_users(allowed_roles=['admins'])
def create_subcategory(request,category_id):
    category = get_object_or_404(Category, id=category_id)
    print(category)
    if request.method == 'POST':
        form = SubcategoryForm(request.POST)
        if form.is_valid():
            new_category = form.save(commit=False)
            new_category.category = category 
            new_category.save()
            messages.success(request, _("New Subcategory created successfully!"))
            return redirect('admins.chatbot') 
        else:
            messages.error(request, _("There was an error creating the Subcategory."))
            return redirect('admins.chatbot') 

@login_required
@allowed_users(allowed_roles=['admins'])
def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    subcategory.delete()

    messages.success(request, _("Subcategory deleted successfully!"))
    return redirect('admins.chatbot')
