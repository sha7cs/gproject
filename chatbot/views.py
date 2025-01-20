from django.shortcuts import render
from users_app.models import UsersModel
from chatbot.models import Category,Subcategory,Question
from django.http import JsonResponse
import json
import openai
from openai import OpenAI
from django.core import serializers

# Initialize OpenAI client
api_key="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"
client = openai.Client(api_key=api_key)

# Step 1: Create the Assistant
def create_assistant():
    assistant = client.beta.assistants.create(
        name="Cafe Marketing Assistant",
        instructions="You are a marketing expert helping a café manager grow their business. Ask follow-up questions to gather details and provide actionable suggestions.",
        tools=[], 
        model="gpt-4o"
    )
    return assistant.id 

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

def run_assistant(thread_id, assistant_id, instructions):
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
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

# Global Assistant ID (create once and reuse)
assistant_id = create_assistant()

def chatbot(request):
    if request.method == 'GET':
         # for html
         categories= Category.objects.all()
         subcategories = Subcategory.objects.all()
         allquestions = Question.objects.all()
         #for script
         categories_json = serializers.serialize('json', categories, use_natural_primary_keys=True)
         subcategories_json = serializers.serialize('json', subcategories, use_natural_primary_keys=True)
         allquestions_json = serializers.serialize('json', allquestions, use_natural_primary_keys=True)

         return render(request, 'chatbot/chatbot.html',{
            'categories': categories,
            'subcategories': subcategories,
            'allquestions': allquestions,
            'categories_json': categories_json,
            'subcategories_json': subcategories_json,
            'allquestions_json': allquestions_json,
        })

    if request.method == 'POST':
        subcategory = request.POST.get('subcategory', '').strip()
        question = request.POST.get('question', '').strip()
        user_response = request.POST.get('response', '').strip()
        question_index = int(request.POST.get('questionIndex', 0))

        user = UsersModel.objects.get(id=1)  # Replace with appropriate user logic
        thread_id = get_or_create_thread(user)

        # Log the assistant's question
        if question:
            add_assistant_message_to_thread(thread_id, question)

        # Log the user's response
        if user_response:
            add_message_to_thread(thread_id, user_response)

        inst =f"""You are a marketing expert helping a café manager in Saudi Arabia. They want friendly and practical advice to improve their marketing.
                After asking 3 or 2 follow-up questions to understand their goals, provide a short and conversational response with key actionable suggestions.
                Keep it concise and avoid formal or structured lists.""" # مره افضل خلت الرد قصير وفكرته واضحة 

         # Fetch subcategory and related questions
        try:
            subcategory = Subcategory.objects.get(name=subcategory)
            questions = subcategory.questions.all()
        except Subcategory.DoesNotExist:
            return JsonResponse({"response": "Invalid subcategory selected."})

        # Determine the next question or generate a final response
        if question_index < questions.count():
            next_question = questions[question_index].text
            return JsonResponse({
                "response": next_question,  # Send the next question
                "questionIndex": question_index + 1,  # Increment index for the next interaction
            })
        else:
            # Generate the final response
            final_message = "Thank you for your responses! Here’s my advice based on your inputs."
            final_response = run_assistant(thread_id, assistant_id, inst)
            return JsonResponse({"response": str(final_response)})

    return JsonResponse({"response": "Invalid request."})

