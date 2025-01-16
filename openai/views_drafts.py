


# api_key = "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"
# client = OpenAI(api_key=api_key)
  
  
  
# user_cafe_info = {
#     "season": "Summer",
#     "daily_sales": 1500,
#     "items": ["Espresso", "Croissant", "Iced Latte"]
# }

# category= "suggest promotion"

# questions = {
#         "Marketing advice": {
#             "Add a new item": [
#                 "What type of item are you thinking of adding (e.g., beverage, dessert)?",
#                 "Do you want suggestions based on current trends or your sales data?"
#             ],
#             "Suggest promotion": [
#                 "How long do you want the promotion to run (e.g., one week, one month)?",
#                 "Do you have a specific type of offer in mind (e.g., seasonal, cultural, general)?"
#             ]
#         },
#         "Analysis": {
#             "Failing item": [
#                 "What item is currently underperforming?",
#                 "Do you have any insights into why this item might not be selling well?"
#             ],
#             "Best time to promote": [
#                 "Do you want to focus on a specific time of day (e.g., morning, evening)?",
#                 "Would you like suggestions based on current sales patterns?"
#             ]
#         }
#     }

# #example 
# session_data = {
#     'category': None,
#     'subcategory': None,
#     'current_question': 0,
#     'answers': []
# }
# sys_message = f"""
#     You are a marketing expert giving advice to a café manager. They want {category}.
#     Based on this, ask follow-up questions one at a time to gather information and provide actionable suggestions.
#     Respond strictly in the following format:
#     - Start by asking one specific follow-up question.
#     - After gathering all required information, give a clear, concise recommendation.
#     Here is some information about the café:
#     - Current season: {user_cafe_info['season']}
#     - Average daily sales: {user_cafe_info['daily_sales']}
#     - Items available: {', '.join(user_cafe_info['items'])}.
#     """

# def send_prompt(syscontent ,user_message):
#     prompt = client.chat.completions.create(
#         messages = [{'role': "system", "content": sys_message},
#                     {"role": "user", "content": user_message },
#                     ],
#         model="gpt-4-turbo", # gpt-4o
#         temperature = 1.2,
#         top_p = 0.9, 
#         frequency_penalty = 0.5, 
#         presence_penalty = 1.0
#     )
#     response = prompt.choices[0].message.content
#     return response


# def chatbot(request):
#     # syscontent = "yor are a marketing assistant to a cafe manager. the cafe is in saudi arabia. Respond in a friendly and professional tone to help the manager handle and grow the cafe."
#     syscontent = sys_message
#     if request.method == 'POST':
#         user_message = request.POST.get('message','').strip()
#         response = send_prompt(syscontent, user_message)
#         return JsonResponse({'message' : user_message , 'response' : response})
#     return render(request , 'chatbot.html')


# # def clear_history(request):
# #     if 'chat_history' in request.session:
# #         del request.session['chat_history']
# #     return JsonResponse({'status': 'success'})

# # i want to make a new offer this week to bring more costumers and increase sales

# import openai

# inst = f"""You are a marketing expert giving advice to a café manager. They want some help in promotions and markeing advices.
#     Based on this, ask follow-up questions one at a time to gather information and provide actionable suggestions.
#     Respond strictly in the following format: 
#     Start by asking one specific follow-up question.
#     After gathering all required information, give a clear, concise recommendation."""


# assistant = openai.beta.assistants.create(
#     name="Marketing assistant",
#     instructions=inst,
#     tools=[{"type": "code_interpreter"}],  # Enables code execution
#     model="gpt-4-turbo"
#     )

# print(assistant.id)



# # view  so each user can call this view and it will be associated with his id?

# thread = openai.beta.threads.create()

# message = openai.beta.threads.messages.create(
#     thread_id=thread.id,
#     role="user",
#     content="give me good promotion for coffe of the day and cookie bites"
# )

# run = openai.beta.threads.runs.create(
#     thread_id=thread.id,
#     assistant_id=assistant.id
# )

# # Fetch responses from the thread
# responses = openai.beta.threads.messages.list(thread_id=thread.id)
# for message in responses:
#     print(message.content)


# openai.api_key = "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"

# # System instructions for the Assistant
# inst = f"""You are a marketing expert giving advice to a café manager. They want help with promotions and marketing advice.
#             Based on this, ask follow-up questions one at a time to gather information and provide actionable suggestions.
#             Respond strictly in the following format: 
#             - Start by asking one specific follow-up question.
#             - After gathering all required information, give a clear, concise recommendation."""

# # Create Assistant with specific instructions
# assistant = openai.beta.assistants.create(
#     name="Marketing Assistant",
#     instructions=inst,
#     tools=[{"type": "code_interpreter"}],  # Enable code execution if necessary
#     model="gpt-4-turbo"
# )

# # Function to create or get an existing thread for the user
# def get_or_create_thread(user):
#     if not user.thread_id:
#         # Create a new thread
#         thread = openai.beta.threads.create()
#         user.thread_id = thread.id  # Save thread_id in user model
#         user.save()
#     else:
#         # Fetch existing thread
#         thread = openai.beta.threads.retrieve(thread_id=user.thread_id)
    
#     return thread.id

# # Function to send user message and receive assistant response
# def send_message_to_assistant(thread_id, user_message):
#     # Send user message
#     openai.beta.threads.messages.create(
#         thread_id=thread_id,
#         role="user",
#         content=user_message
#     )
    
#     # Fetch assistant's response
#     responses = openai.beta.threads.messages.list(thread_id=thread_id)

#     # Convert to list and access the latest message
#     messages = list(responses)
#     if messages:
#         latest_message = messages[-1]
#         content = latest_message.content

#         # Check if content is a TextContentBlock and extract its value
#         if isinstance(content, list) and len(content) > 0 and isinstance(content[0], TextContentBlock):
#             # Extract the text value from the first TextContentBlock
#             assistant_response = content[0].text.value
#         else:
#             # Fallback: convert content to string
#             assistant_response = str(content)

#         return assistant_response

#     return "No response from the assistant."

# # View function for handling the chatbot interaction
# def chatbot(request):
#     if request.method == 'POST':
#         user_message = request.POST.get('message', '').strip()
#         # user_email = request.POST.get('email', '').strip()
#         user_email = 'kimy1395@gmail.com'

#         # Fetch the user from the database (assuming email is unique)
#         user = UsersModel.objects.get(email=user_email)

#         # Get or create a thread for the user
#         thread_id = get_or_create_thread(user)

#         # Send user message to assistant and get response
#         assistant_response = send_message_to_assistant(thread_id, user_message)

#         # Save the conversation in the ChatSession model
#         # chat_session, created = ChatSession.objects.get_or_create(user=user, thread_id=thread_id)
#         # chat_session.messages.append({"role": "user", "content": user_message})
#         # chat_session.messages.append({"role": "assistant", "content": assistant_response})
#         # chat_session.save()

#         # Return the response to the frontend
#         return JsonResponse({'message': user_message, 'response': assistant_response})

#     return render(request, 'chatotty.html')

# def get_or_create_thread(request):
#     thread_id = request.session.get("thread_id")
#     if not thread_id:
#         # Create a new thread and store its ID in the session
#         thread = openai.beta.threads.create()
#         thread_id = thread.id
#         request.session["thread_id"] = thread_id
#     return thread_id

# def extract_assistant_response(response_data):
#     """Extracts the assistant's response text from the message list."""
#     for message in response_data['data']:
#         if message['role'] == 'assistant' and 'content' in message:
#             # Look for text blocks and return the concatenated text
#             text_content = [block['text']['value'] for block in message['content'] if block['type'] == 'text']
#             return " ".join(text_content)
#     return "No response from the assistant."

# def chatbot(request):
#     if request.method == 'POST':
#         user_message = request.POST.get('message', '').strip()
#         category = request.POST.get('category', '').strip()

#         if not user_message or not category:
#             return JsonResponse({'response': "Invalid input. Please try again."})

#         # Get or create a thread ID for the session
#         thread_id = get_or_create_thread(request)

#         try:
#             # Send the user message to the assistant
#             openai.beta.threads.messages.create(
#                 thread_id=thread_id,
#                 role="user",
#                 content=user_message,
#             )

#             # Retrieve the assistant's latest response
#             responses = openai.beta.threads.messages.list(thread_id=thread_id)
#             # Assuming the API returns a JSON response with 'data' that contains message objects
#             assistant_response = extract_assistant_response(responses)

#             return JsonResponse({'response': assistant_response})

#         except Exception as e:
#             return JsonResponse({'response': f"Error: {str(e)}"}, status=500)

#     return render(request, 'chatotty.html')
