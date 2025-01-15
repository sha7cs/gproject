import os
from openai import OpenAI


# api_key = os.environ.get("OPENAI_API_KEY")  # Get API key from environment
# if not api_key:
#     raise ValueError("Missing OpenAI API key. Set it as an environment variable.")

# client = OpenAI(api_key=api_key)

# old system prompt = "you are an assistant for a cafe manager to help him woth marketing and analysis"

# marketing advice               analysis 
# add a new item               -    # failing item 
# suggest promotion            -    # best time to promote 
# lets chat about marketing    -    # overall analysis (رد موحد )
# other

api_key = "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"
client = OpenAI(api_key=api_key)




def create_sysmessage(category1 , category2):
    # if user chose this sys message = this
    syscontent= f"You are now providing {category1}. Focus on {category2}."
           
        
user_cafe_info = {
    "season": "Summer",
    "daily_sales": 1500,
    "items": ["Espresso", "Croissant", "Iced Latte"]
}

category= "suggest promotion"

sys_message = f"""
You are a marketing expert giving advice to a café manager. They want a {category}. 
Based on this, ask follow-up questions and provide suggestions. 
Here is some information about the café:
- Current season: {user_cafe_info['season']}
- Average daily sales: {user_cafe_info['daily_sales']}
- Items available: {', '.join(user_cafe_info['items'])}.
"""

def send_prompt(sys_message, user_message):
    response = client.chat.completions.create(
        messages = [{'role': "system", "content": sys_message},
                   {"role": "user", "content": user_message }],
        model="gpt-3.5-turbo",
        temperature = 1.2,
        top_p = 0.9, 
        frequency_penalty = 0.5, 
        presence_penalty = 1.0
    )
    response = response.choices[0].message.content
    return response

# syscontent = "yor are an assistant to a cafe manager. the cafe is in saudi arabia. Respond in a friendly and professional tone"
# user_content = "suggest a new item for the summer."


def send_prompt_assistant():
    assistant = client.beta.assistants.create(
    name = "marketing assistant",
    instructions = "",
    
    )


user_message = None
user_message = user_message.strip() if user_message else "The manager has selected their preferred category."

print(send_prompt(sys_message, user_message))

#export OPENAI_API_KEY="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"




# guides to enhance chat:
# "Respond in a friendly and professional tone"
# Frequency Penalty: Discourages the model from repeating the same words or phrases. Range: -2.0 to 2.0. Higher values reduce repetition. Lower or negative values encourage repetition.
# Presence Penalty: Encourages the model to introduce new topics or ideas. Range: -2.0 to 2.0. Higher values make the model explore new areas. Lower values stick to familiar concepts.
# Context and Conversation History 
# Top-p (Nucleus Sampling): Controls the diversity of responses by selecting tokens from a subset of probabilities.


# Test 1: Creative Writing: (common)
# temperature = 1.2, top_p = 0.9, frequency_penalty = 0.5, presence_penalty = 1.0.
# this was the input:
# syscontent = "yor are an assistant to a cafe manager. the cafe is in saudi arabia. Respond in a friendly and professional tone"
# user_content = "suggest a new item for the summer."
# and this is the output:
# Certainly! How about introducing a refreshing iced mint lemonade to the menu for the summer season? It's a popular choice during hot weather and would be a great addition to help our customers cool down and enjoy their time at the cafe. Let me know if you'd like more details on how we can incorporate this item into our menu!