from django.shortcuts import render
from users_app.models import UsersModel
from chatbot.models import Category,Subcategory,Question
from django.http import JsonResponse
import json
import openai
from openai import OpenAI
from django.core import serializers
from django.utils. translation import gettext_lazy as _
from django. utils. translation import get_language, activate, gettext

from django.utils.translation import activate
from django.http import HttpResponseRedirect
from django.urls import reverse

def set_language(request):
    language = request.GET.get('language')
    if language:
        activate(language)
    return HttpResponseRedirect(reverse('chatbot'))  # Or whichever URL you want to redirect to

# Initialize OpenAI client
api_key="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"
client = openai.Client(api_key=api_key)

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

def run_assistant(thread_id, instructions):
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id="asst_2vl0GWgN3eO4zit970iZln8m",
        instructions=instructions
    )

    if run.status == "completed":
        # Retrieve the assistant's response messages
        messages = client.beta.threads.messages.list(thread_id=thread_id)

        # Extract assistant's response from the messages
        for msg in messages:
            if msg.role == "assistant":
                assistant_response = "".join(
                    block.text.value for block in msg.content if block.type == "text"
                )
                return assistant_response
    return "No response from the assistant."

# # Global Assistant ID (create once and reuse)
# assistant_id = create_assistant()
         
import traceback
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.translation import get_language
from parler.models import TranslatableModel
from parler.utils import get_active_language_choices

@csrf_exempt
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


         return render(request, 'chatbot/chatbot.html',{
            'categories': categories,
            'subcategories': subcategories,
            'allquestions': allquestions,
            'categories_json': categories_json,
            'subcategories_json': subcategories_json,
            'allquestions_json': allquestions_json,
            'language': language,
        })
    try:
        if request.method == 'POST':
            subcategory = request.POST.get('subcategory', '').strip()
            question = request.POST.get('question', '').strip()
            user_response = request.POST.get('response', '').strip()
            question_index = int(request.POST.get('questionIndex', 0))

            user = UsersModel.objects.get(id=1)  # Replace with actual user logic
            thread_id = get_or_create_thread(user)

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
                    "questionIndex": question_index + 1,
                })
            else:
                final_response = run_assistant(thread_id, inst)
                return JsonResponse({"response": str(final_response)})

        return JsonResponse({"error": "Invalid request method."}, status=405)
    
    except Exception as e:
        error_message = traceback.format_exc()  # Get full error details
        print("Backend Error:", error_message)  # Log error in Django console
        return JsonResponse({"error": "Server error. Check Django logs for details."}, status=500)

  