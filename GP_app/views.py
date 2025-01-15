from django.shortcuts import render

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


import openai

openai.api_key = "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"

inst = f"""You are a marketing expert giving advice to a café manager. They want some help in promotions and markeing advices.
    Based on this, ask follow-up questions one at a time to gather information and provide actionable suggestions.
    Respond strictly in the following format: 
    Start by asking one specific follow-up question.
    After gathering all required information, give a clear, concise recommendation."""


assistant = openai.beta.assistants.create(
    name="Marketing assistant",
    instructions="You help users analyze their datasets and generate insights.",
    tools=[{"type": "code_interpreter"}],  # Enables code execution
    model="gpt-4-turbo"
    )

print(assistant.id)



# view  so each user can call this view and it will be associated with his id?

thread = openai.beta.threads.create()

message = openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="give me good promotion for coffe of the day and cookie bites"
)

run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# Fetch responses from the thread
responses = openai.beta.threads.messages.list(thread_id=thread.id)
for message in responses:
    print(message.content)

