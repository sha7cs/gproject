from django.shortcuts import render
from django.http import JsonResponse
from users_app.models import UsersModel
import json
import openai
from openai import OpenAI

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


# Initialize OpenAI client
api_key="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"
client = openai.Client(api_key=api_key)

# Step 1: Create the Assistant
def create_assistant():
    assistant = client.beta.assistants.create(
        name="Cafe Marketing Assistant",
        instructions="You are a marketing expert helping a café manager grow their business. Ask follow-up questions to gather details and provide actionable suggestions.",
        tools=[],  # Add tools if needed
        model="gpt-4o"
    )
    return assistant.id  # Return the assistant ID

# Step 2: Create a Thread
def get_or_create_thread(user):
    if not user.thread_id:
        # Create a new thread if thread_id is not set
        thread = client.beta.threads.create()
        user.thread_id = thread.id  # Save thread_id to the user model
        user.save()
    else:
        try:
            # Ensure the existing thread still exists
            client.beta.threads.retrieve(thread_id=user.thread_id)
        except Exception as e:
            # Handle missing or invalid thread by creating a new one
            print(f"Thread retrieval failed: {e}")
            thread = client.beta.threads.create()
            user.thread_id = thread.id
            user.save()
    
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

# Step 4: Run the Assistant and Get Response
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
                # Access the `value` field inside `TextContentBlock`
                assistant_response = "".join(
                    block.text.value for block in msg.content if block.type == "text"
                )
                return assistant_response

    # Return a default message if no assistant response is found
    return "No response from the assistant."


# Global Assistant ID (create once and reuse)
assistant_id = create_assistant()

SUBCATEGORY_QUESTIONS = {
    "Marketing Advice": {
        "Social Media Strategy": [
            "What social media platforms do you currently use?",
            "What is your target audience?",
            "Do you have a budget for social media ads?",
        ],
        "Content Marketing": [
            "What type of content do you create?",
            "What are your content marketing goals?",
            "Do you analyze content performance?",
        ],
    },
    "Analysis": {
        "Sales Performance": [
            "What is your average monthly revenue?",
            "What are your best-selling items?",
            "Do you track seasonal sales trends?",
        ],
        "Customer Feedback": [
            "How do you collect customer feedback?",
            "What are common customer complaints?",
            "Do you respond to customer reviews?",
        ],
    },
}




def chatbot(request):
    if request.method == 'GET':
        return render(request, 'chatotty.html', {'questions': SUBCATEGORY_QUESTIONS})

    if request.method == 'POST':
        category = request.POST.get('category', '').strip()
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

        inst =f"""You are a marketing expert giving advice to a café manager in Saudi Arabia. They want help with promotions and marketing advice.
                    Based on this, you asked 3 or 2 follow-up questions to gather information from the user and provide actionable suggestions after the last question is answered.
                    Respond strictly in the following format: 
                    - Start by asking one specific follow-up question.
                    - After gathering all required information, give a clear, concise recommendation."""

        # Get the next question or generate a final response
        questions = SUBCATEGORY_QUESTIONS.get(category, {}).get(subcategory, [])
        if question_index < len(questions):
            next_question = questions[question_index]
            return JsonResponse({
                "response": next_question,  # Send the next question
                "questionIndex": question_index + 1,  # Increment index for the next interaction
            })
        else:
            final_message = "Thank you for your responses! Here’s my advice based on your inputs."
            final_response = run_assistant(thread_id, assistant_id, inst)
            return JsonResponse({"response": final_response})

    return JsonResponse({"response": "Invalid request."})


# Chatbot view


#   instruction = f"""
#         You are a marketing expert giving advice to a café manager in Saudi Arabia. They want a {category}, specifically {subcategory}.
#         Here are their responses: {responses}.
#         Please provide them with a clear professional answer that considers the given context and ask them if they need further help. Make it short, clear, useful, and from a business standpoint.
#         """


# let's orgnaize our thoughts:
# design of messages in thread should be:
# first assistant: choose category and subcategory, then i will ask you a few follow up questions!
# second user: category: ... , subcategory:... 
# third assistant: Q1
# fourth user: response[0]
# until questions end maybe with the last response we attach a string that says ", now please provide me with a clear response that follows the context."
# final response assistant: ... 

# first thread message appended is after user chooses category and subcategory. 
# but how is the structure of the messages should it be user,assistant,user, assistant in order? 
# if so we need to consider it but we cant add the assistnat message?! #lets say it's not in order 
# as i said first thread message appended is after user chooses category and subcategory. 
# then it would be question: ... ? , my answer: ... 
# when they are done we send this :
# based on our previouse recent conversation, Please provide me with a clear professional answer that considers the given context
