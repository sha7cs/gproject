from django.shortcuts import render
from authentication_app.models import UserProfile
from promotions.models import Category,Subcategory,Question, DailyAdvice
from django.http import JsonResponse
import json
import openai
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language, activate
from django.http import HttpResponseRedirect
from django.urls import reverse
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
import pandas as pd
from django.conf import settings
import ast
import traceback
from parler.utils import get_active_language_choices
import datetime
import markdown

def analyze_sales_data():
    csv_path = 'Data/Sales_ARS.csv'
    df = pd.read_csv(csv_path)
    print("✅ CSV loaded successfully from:", csv_path)

    df['business_date'] = pd.to_datetime(df['business_date'], format='%d/%m/%Y')
    df['day_of_month'] = df['business_date'].dt.day

    best_days = df.groupby('day_of_month')['total_price'].sum()
    best_days_range = best_days.sort_values(ascending=False).head(5).index.tolist()
    best_days_range = sorted([int(day) for day in best_days_range])


    best_time_range = f"{best_days_range[0]}-{best_days_range[-1]} " + _("of the month") if len(best_days_range) > 1 else f"{best_days_range[0]} " + _("of the month")

    df['detailed_orders'] = df['detailed_orders'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    products = []
    for order_list in df['detailed_orders']:
        if isinstance(order_list, list):
            for item in order_list:
                products.append(item['item'])

    products_df = pd.DataFrame(products, columns=['product'])
    best_product = products_df['product'].value_counts().idxmin()  

    print(" Best Days to Promote:", best_time_range)
    print(" Best Product to Discount:", best_product)

    return {"best_time": best_time_range, "best_product": best_product}

def set_language(request, urlname):
    language = request.GET.get('language')
    if language:
        activate(language)
        request.session['django_language'] = language
    # Redirect to the given URL name
    return HttpResponseRedirect(reverse(urlname))
 
# Initialize OpenAI client
client = openai.Client(api_key = settings.OPENAI_API_KEY)

# Step 2: Create a Thread
def get_or_create_thread(user):
    if not user.thread_id:
        # Create a new thread if thread_id is not set
        thread = client.beta.threads.create()
        user.thread_id = thread.id  
        user.save()
    else:
        client.beta.threads.retrieve(thread_id=user.thread_id)
    return user.thread_id

# Step 3: Add a Message to the Thread
def add_message_to_thread(thread_id, user_message):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

def add_assistant_message_to_thread(thread_id, assistant_message):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content=assistant_message
    )
import time

def run_assistant(thread_id, instructions):
    try:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id="asst_2vl0GWgN3eO4zit970iZln8m",
            instructions=instructions
        )
        retries = 0
        max_retries=3
        while run.status != "completed" and retries < max_retries:
            retries += 1
            print(f"Run status is {run.status}. Waiting for completion...")
            time.sleep(20)  # Wait for the specified delay (in seconds)
            run = client.beta.threads.runs.get(run_id=run.id)

        if run.status != "completed":
            return f"Run status is {run.status}. Assistant hasn't finished processing after {max_retries} retries."

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        if not messages:
            return "No messages found in the thread."

        for msg in messages:
            if msg.role == "assistant":
                assistant_response = "".join(
                    block.text.value for block in msg.content if block.type == "text"
                )
                return assistant_response  # Only return the assistant's response text
        return "No response from the assistant."
    except Exception as e:
            return f"An error occurred: {str(e)}"  



# ####### firebase data integration: 
# firebaseConfig = {
#     'apiKey': "AIzaSyDM_4QRe0nk1grjMGXlkiy8zHmuSJXDCdw",
#     'authDomain': "cafe-data-project-106c5.firebaseapp.com",
#     'databaseURL': "https://cafe-data-project-106c5-default-rtdb.firebaseio.com",
#     'projectId': "cafe-data-project-106c5",
#     'storageBucket': "cafe-data-project-106c5.firebasestorage.app",
#     'messagingSenderId': "693566101460",
#     'appId': "1:693566101460:web:b7844759b6275898ab6841",
#     'measurementId': "G-B1GWW1BPYB"
# };

# firebase = pyrebase.initialize_app(firebaseConfig)
# firebase_db = firebase.database()


@login_required
@allowed_users(allowed_roles=['normal_user','admins'])
def chatbot(request):
    if request.method == 'GET':
         categories= Category.objects.all()
         subcategories = Subcategory.objects.all()
         allquestions = Question.objects.all()
         language = get_language()

         categories_json = json.dumps([
        {'id': category.pk, 'category': category.safe_translation_getter('category', any_language=True)}
        for category in categories
        ])
         subcategories_json = json.dumps([
            {'id': subcategory.pk, 'subcategory': subcategory.safe_translation_getter('subcategory', any_language=True), 'category': subcategory.category_id}
            for subcategory in subcategories
        ])
         allquestions_json = json.dumps([
            {'id': question.pk, 'question': question.safe_translation_getter('question', any_language=True), 'subcategory': question.subcategory_id}
            for question in allquestions
        ])
         
         ####heres the card content stuff 
         today = datetime.date.today()
         total_advice = DailyAdvice.objects.count()

         if total_advice == 0:
             advice_entry = None
         else:
            advice_index = today.timetuple().tm_yday % total_advice
            advice_entry = DailyAdvice.objects.all().order_by('id')[advice_index]
            advice_entry.set_current_language('en')
            
         advice= advice_entry if advice_entry else 'No advice available'

         #analysis cards data  
         analysis_results = analyze_sales_data()
         
         return render(request, 'layout/promotions.html',{
            'categories': categories,
            'subcategories': subcategories,
            'allquestions': allquestions,
            'categories_json': categories_json,
            'subcategories_json': subcategories_json,
            'allquestions_json': allquestions_json,
            'language': language,
            'advice':advice,
            'best_time': analysis_results['best_time'],
            'best_product': analysis_results['best_product']
        })
    try:
        if request.method == 'POST':
            subcategory = request.POST.get('subcategory', '').strip()
            question = request.POST.get('question', '').strip()
            user_response = request.POST.get('response', '').strip()
            question_index = int(request.POST.get('questionIndex'))
            
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            thread_id = get_or_create_thread(user_profile)

            if question:
                add_assistant_message_to_thread(thread_id, question)
            if user_response:
                add_message_to_thread(thread_id, user_response)

            inst = """You are a marketing expert helping a café manager in Saudi Arabia.
                      Ask 2-3 follow-up questions before providing concise marketing advice."""
           
            try:
               subcategory = Subcategory.objects.filter(
                        translations__language_code__in=get_active_language_choices(),
                        translations__subcategory=subcategory
                    ).first()
               questions = subcategory.questions.filter(
                    translations__language_code__in=get_active_language_choices()
                )
            except Subcategory.DoesNotExist:
                return JsonResponse({"error": "Invalid subcategory selected."}, status=400)

            if question_index < questions.count():
                next_question = questions[question_index].question
                return JsonResponse({
                    "response": next_question,
                    "questionIndex": question_index + 2,  # Increment correctly
                })
              
            elif question_index == questions.count():
                # Only generate assistant response once all questions are answered
                final_response = run_assistant(thread_id, inst)
                return JsonResponse({"response": markdown.markdown(str(final_response))})
            else:
                # No more questions
                return JsonResponse({"response": "Thank you! The process is complete."})
            
        return JsonResponse({"error": "Invalid request method."}, status=405)
    
    except Exception as e:
        error_message = traceback.format_exc()  # Get full error details
        print("Backend Error:", error_message)  # Log error in Django console
        return JsonResponse({"error": "Server error. Check Django logs for details."}, status=500)
from django.template.loader import render_to_string

