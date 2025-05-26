from random import choice
from openai import OpenAI,AzureOpenAI
from dotenv import load_dotenv
import os
load_dotenv()
#openai
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



#azure openai
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# 聊天示例
response = client.chat.completions.create(
    model= 'gpt-4o',
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "how to play basketball"},
    ]
)

print(f"Response: {response.choices[0].message.content}")