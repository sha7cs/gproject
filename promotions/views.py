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
from authentication_app.decorators import allowed_users, admin_only, unauthenticated_user,approved_user_required
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
import pandas as pd
from django.conf import settings
import ast
import traceback
from parler.utils import get_active_language_choices
import datetime
import markdown
import sqlite3
import requests
from promotions.models import Event

from analysis.views import user_data

DB_PATH = "sales_data.db"


def analyze_sales_data(request):
    try:
        # Get the user's uploaded file
        user_profile = UserProfile.objects.get(user=request.user)
        user_file = user_profile.data_file
        
        if not user_file:
            return {"error": "User has not uploaded a CSV file."}

        # Read the CSV into a pandas DataFrame
        df = pd.read_csv(user_file.path)
        df['business_date'] = pd.to_datetime(df['business_date'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['business_date', 'total_price'])

        # Best days to promote (group by day of the month)
        df['day_of_month'] = df['business_date'].dt.day
        best_days = df.groupby('day_of_month')['total_price'].sum()
        best_days_range = best_days.sort_values(ascending=False).head(5).index.tolist()
        best_days_range = sorted([int(day) for day in best_days_range])

        if len(best_days_range) > 1:
            best_time_range = f"{best_days_range[0]}-{best_days_range[-1]} of the month"
        elif best_days_range:
            best_time_range = f"{best_days_range[0]} of the month"
        else:
            best_time_range = _("No data available",0)

        # Least selling product
        df['detailed_orders'] = df['detailed_orders'].apply(lambda x: json.loads(x.replace("'", "\"")) if isinstance(x, str) else [])
        products = []
        for order_list in df['detailed_orders']:
            if isinstance(order_list, list):
                for item in order_list:
                    products.append(item.get('item'))

        products_df = pd.DataFrame(products, columns=['product'])
        best_product = products_df['product'].value_counts().idxmin() if not products_df.empty else "No data available"

        return {
            "best_time": best_time_range,
            "best_product": best_product
        }

    except Exception as e:
        return {"error": str(e)}




API_KEY = 'iQsiUvz77fut0nlpqGmsEBghzWCIbeIW'
YEAR = datetime.datetime.today().year

events_data = {
    "Founding Day": {
        "key": "Saudi Founding Day",
        "ar": "يوم التأسيس"
    },
    "Flag Day": {
        "key": "Saudi Flag Day",
        "ar": "يوم العلم السعودي"
    },
    "Eid al-Fitr": {
        "key": "Eid al-Fitr",
        "ar": "عيد الفطر"
    },
    "Eid al-Adha": {
        "key": "Eid al-Adha",
        "ar": "عيد الأضحى"
    },
    "Saudi National Day": {
        "key": "Saudi National Day",
        "ar": "اليوم الوطني السعودي"
    }
    
}



def get_events_from_api():
    url = f"https://calendarific.com/api/v2/holidays?&api_key={API_KEY}&country=SA&year={YEAR}"
    response = requests.get(url)
    data = response.json()

    events = []
    current_lang = get_language()  # 'ar' or 'en'

    if 'response' in data and 'holidays' in data['response']:
        for holiday in data['response']['holidays']:
            api_name = holiday['name']
            if api_name in events_data:
                details = events_data[api_name]
                name_display = details['ar'] if current_lang == 'ar' else details['key']
                date_miladi = holiday['date']['iso']
                events.append({
                    'event_name': name_display,
                    'gregorian_date': pd.to_datetime(date_miladi, utc=True)
                })

    
    event_objects = Event.objects.all()
    for ev in event_objects:
        ev.set_current_language(current_lang)
        events.append({
            'event_name': ev.name,
            'gregorian_date': pd.to_datetime(ev.date)
        })

    return pd.DataFrame(events)


def get_next_event():
    df = get_events_from_api()

    today = pd.to_datetime(datetime.datetime.utcnow()).tz_localize('UTC')
    df['gregorian_date'] = pd.to_datetime(df['gregorian_date'], utc=True)
    upcoming_events = df[df['gregorian_date'] >= today].sort_values('gregorian_date')

    if not upcoming_events.empty:
        next_event = upcoming_events.iloc[0]
        days_remaining = (next_event['gregorian_date'].date() - today.date()).days  

        current_lang = get_language()
        event_name = next_event['event_name']

        return {
            "event_name": event_name,
            "event_date": next_event['gregorian_date'].strftime('%Y-%m-%d'),
            "days_remaining": days_remaining
        }
    
    return None


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
            thread_id    = thread_id,
            assistant_id = "asst_2vl0GWgN3eO4zit970iZln8m",
            instructions = instructions
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
def marketing_advice():
    today = datetime.date.today()
    total_advice = DailyAdvice.objects.count()

    if total_advice == 0:
        advice_entry = None 
    else:
        advice_index = today.timetuple().tm_yday % total_advice
        advice_entry = DailyAdvice.objects.all().order_by('id')[advice_index]
    # advice_entry.set_current_language('en')
    
    advice = advice_entry if advice_entry else _('No advice available')
    if advice_entry:
        advice_title = _(advice_entry.title)  # Translating title
        advice_text = _(advice_entry.advice)  # Translating advice text
    else:
        advice_title = advice_text = None
    return advice_title, advice_text
    

@login_required
@allowed_users(allowed_roles=['normal_user','admins'])
@approved_user_required
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
         advice_title, advice_text = marketing_advice()
         #analysis cards data  
         analysis_results = analyze_sales_data(request)
         next_event = get_next_event()
         return render(request, 'promotions/promotions.html',{
            'categories': categories,
            'subcategories': subcategories,
            'allquestions': allquestions,
            'categories_json': categories_json,
            'subcategories_json': subcategories_json,
            'allquestions_json': allquestions_json,
            'language': language,
            'advice_title': advice_title,
            'advice_text':advice_text,
            'best_time': analysis_results.get('best_time', 'No data available'),
            'best_product': analysis_results.get('best_product', 'No data available'),
            'next_event': next_event  
        })
    try:
        if request.method == 'POST':
            subcategory = request.POST.get('subcategory', '').strip()
            question = request.POST.get('question', '').strip()
            user_response = request.POST.get('response', '').strip()
            question_index = int(request.POST.get('questionIndex'))
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            thread_id = get_or_create_thread(user_profile)
            
            # اذا موجودة بالبوست احفظها بالسشن اذا مو موجودة حط اللي بالسشن داخل الفاريبل كاتقوري
            category = request.POST.get('category')
            if category != 'null':
                request.session['category'] = category
            else:
                category = request.session.get('category')
            if not category:
                return JsonResponse({"error": "Category is missing. Please reselect the category."}, status=400)

            if question:
                add_assistant_message_to_thread(thread_id, question)
            if user_response:
                add_message_to_thread(thread_id, user_response)
            # نجيب بيانات االمستخدم للشات
            context_data = user_data(request) 
            user_analysis_summary = f"""
                                        - إجمالي المبيعات: {context_data['total_sales']}
                                        - عدد العمليات: {context_data['total_transactions']}
                                        - المنتج الأفضل مبيعًا: {context_data['best_seller']}
                                        - معدل نمو المبيعات: {context_data['sales_growth_rate']}%
                                        - أعلى مبيعات بالفئات: {', '.join(f"{label}: {value}" for label, value in zip(context_data['category_labels'], context_data['category_data']))}
                                        - التوقعات المستقبلية: {context_data['predicted_sales']} (بدقة {context_data['prediction_accuracy']}%)
                                        """
            if category in ["analysis", "تحليل"]:
                inst = f"""أنت محلل بيانات محترف تساعد مدير مقهى في السعودية يفهم أداء مشروعه من ناحية الأرقام.
                راح توصلك بيانات المقهى على شكل أرقام (مبيعات، منتجات، نمو..الخ).
                عطي المستخدم تحليل واضح وبسيط يفهمه بسهولة، بدون مصطلحات صعبة.
                ركّز على وش قاعد يصير، هل الأمور ماشية صح؟ وش أبرز الملاحظات؟ وش ممكن يتعدل؟
                بعد التحليل، إذا المستخدم سألك عن شيء زيادة، جاوبه عادي.

                بيانات المستخدم:
                {user_analysis_summary}
                """
            elif category in ["marketing", "نصائح تسويقية"]:
                inst = """أنت خبير تسويق تساعد مدير مقهى في السعودية. عندك خبرة واسعة بأساليب التسويق والعروض اللي تمشي في السوق السعودي وذوق الزبائن.
                راح توصلك معلومات من المستخدم على شكل أسئلة وأجوبتها داخل المحادثة (زي محادثة سابقة)، فاقرأها وافهم وش هدفه أو وش يفكر فيه، بعدين عطه اقتراحات عملية تنفعه فعلاً.
                ردك يكون كأنك تسولف معاه، لا تستخدم لغة رسمية ولا تنسيق نقاط. خلك واضح، مباشر، وودّي، وخلّي الرد سهل يقدر يطبقه في الواقع.
                الرد يكون مختصر (أقل من 200 كلمة)، ويركز على أفكار تسويقية قابلة للتطبيق.
                """ 
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
                    "questionIndex": question_index + 2, 
                })             
            else:
                # Only generate assistant response once all questions are answered
                final_response = run_assistant(thread_id, inst)
                return JsonResponse({"response": markdown.markdown(str(final_response))})
                
        return JsonResponse({"error": "Invalid request method."}, status=405)
    
    except Exception as e:
        error_message = traceback.format_exc()  # Get full error details
        print("Backend Error:", error_message)  # Log error in Django console
        return JsonResponse({"error": "Server error. Check Django logs for details."}, status=500)
    
from django.shortcuts import redirect


@login_required
def delete_thread(request):
    if request.method == 'POST':
        profile = request.user.userprofile
        thread_id = profile.thread_id
        if thread_id:
            profile.thread_id = None
            profile.save()
        return redirect('promotions') 