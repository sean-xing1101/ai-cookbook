from multiprocessing.connection import answer_challenge

from openai import OpenAI,AzureOpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

#azure openai
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)
model="gpt-4o"

class CheckIfBusinessEvent(BaseModel):
    if_business: bool
    confidence: float

def check_if_business_question(question: str) -> tuple[bool, float]:
    system_prompt = "你是一个笔记本厂商分类判断助手，请判断以下内容是否为业务相关问题。返回是否是业务问题和一个0到1之间的置信度评分。"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    completion =  client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=CheckIfBusinessEvent
    )
    answer = completion.choices[0].message.parsed
    return answer.if_business, answer.confidence

# question= '我想查看一下在nova平台近两天测试了多少case'
# question2 = '我想看一下今天的天气'
# completion = check_if_business_question(question)
# print(completion.if_business)
# print(completion.confidence)

