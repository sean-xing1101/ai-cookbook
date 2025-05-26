from pydantic import BaseModel

from openai import AzureOpenAI
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


# --------------------------------------------------------------
# Step 1: Define the response format in a Pydantic model
# --------------------------------------------------------------


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

class QueryEvent(BaseModel):
    product: str
    date: str
    plaform: list[str]
# --------------------------------------------------------------
# Step 2: Call the model
# --------------------------------------------------------------

completion = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extract the query."},
        {
            "role": "user",
            "content": "帮我查一下Baymax14近3天的在Nova测试进展.",
        },
    ],
    response_format=QueryEvent,
)

# --------------------------------------------------------------
# Step 3: Parse the response
# --------------------------------------------------------------

event = completion.choices[0].message.parsed
print(event)
