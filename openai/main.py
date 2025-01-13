import os
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")  # Get API key from environment

if not api_key:
    raise ValueError("Missing OpenAI API key. Set it as an environment variable.")

client = OpenAI(api_key=api_key)
# old system prompt = "you are an assistant for a cafe manager to help him woth marketing and analysis"

# marketing advice               analysis 
# add a new item               -    # failing item 
# suggest promotion            -    # best time to promote 
# lets chat about marketing    -    # overall analysis (رد موحد )
# other


def create_sysmessage():
    # if user chose this sys message = this
    pass
    
def send_prompt(sys_message, user_message):
    response = client.chat.completions.create(
        messages = [{'role': "system", "content": sys_message},
                   {"role": "user", "content": user_message }],
        model="gpt-3.5-turbo",
    )
    response = response.choices[0].message.content
    return response

syscontent = "you are a chatting bot"
user_content = "say test"
print(send_prompt(syscontent, user_content))

#export OPENAI_API_KEY="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"