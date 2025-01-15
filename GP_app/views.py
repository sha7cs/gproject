from django.shortcuts import render
from django.http import JsonResponse
import json
from openai import OpenAI

# Create your views here.

def index(request):
    return render(request, 'base.html' )

def home(request):
    return render(request, 'layout/dashboard.html' )

def analytics_view(request):
    return render(request, 'layout/analytics.html' )

def promotions_view(request):
    return render(request, 'layout/promotions.html' )

def reports_view(request):
    return render(request, 'layout/reports.html' )

def welcome_view(request):
    return render(request, 'welcome.html' )



api_key = "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"
client = OpenAI(api_key=api_key)
  
  
  
user_cafe_info = {
    "season": "Summer",
    "daily_sales": 1500,
    "items": ["Espresso", "Croissant", "Iced Latte"]
}

category= "suggest promotion"

questions = {
        "Marketing advice": {
            "Add a new item": [
                "What type of item are you thinking of adding (e.g., beverage, dessert)?",
                "Do you want suggestions based on current trends or your sales data?"
            ],
            "Suggest promotion": [
                "How long do you want the promotion to run (e.g., one week, one month)?",
                "Do you have a specific type of offer in mind (e.g., seasonal, cultural, general)?"
            ]
        },
        "Analysis": {
            "Failing item": [
                "What item is currently underperforming?",
                "Do you have any insights into why this item might not be selling well?"
            ],
            "Best time to promote": [
                "Do you want to focus on a specific time of day (e.g., morning, evening)?",
                "Would you like suggestions based on current sales patterns?"
            ]
        }
    }

#example 
session_data = {
    'category': None,
    'subcategory': None,
    'current_question': 0,
    'answers': []
}
sys_message = f"""
    You are a marketing expert giving advice to a café manager. They want {category}.
    Based on this, ask follow-up questions one at a time to gather information and provide actionable suggestions.
    Respond strictly in the following format:
    - Start by asking one specific follow-up question.
    - After gathering all required information, give a clear, concise recommendation.
    Here is some information about the café:
    - Current season: {user_cafe_info['season']}
    - Average daily sales: {user_cafe_info['daily_sales']}
    - Items available: {', '.join(user_cafe_info['items'])}.
    """

def send_prompt(syscontent ,user_message):
    prompt = client.chat.completions.create(
        messages = [{'role': "system", "content": sys_message},
                    {"role": "user", "content": user_message },
                    ],
        model="gpt-4-turbo", # gpt-4o
        temperature = 1.2,
        top_p = 0.9, 
        frequency_penalty = 0.5, 
        presence_penalty = 1.0
    )
    response = prompt.choices[0].message.content
    return response


def chatbot(request):
    # syscontent = "yor are a marketing assistant to a cafe manager. the cafe is in saudi arabia. Respond in a friendly and professional tone to help the manager handle and grow the cafe."
    syscontent = sys_message
    if request.method == 'POST':
        user_message = request.POST.get('message','').strip()
        response = send_prompt(syscontent, user_message)
        return JsonResponse({'message' : user_message , 'response' : response})
    return render(request , 'chatbot.html')


# def clear_history(request):
#     if 'chat_history' in request.session:
#         del request.session['chat_history']
#     return JsonResponse({'status': 'success'})

# i want to make a new offer this week to bring more costumers and increase sales