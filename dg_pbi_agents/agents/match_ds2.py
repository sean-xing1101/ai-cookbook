from openai import OpenAI,AzureOpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from dg_pbi_agents.config.donfig_info import datasets
load_dotenv()

#azure openai
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)
model="gpt-4o"

datasets_info = datasets

class OutPutDsInfo(BaseModel):
    dataset_id: str
    dataset_name: str
    dataset_description: str

def select_dataset(question: str) -> tuple[bool, float]:
    descriptions = "\n".join([f"{ds['name']}: {ds['desc']} id:{ds['id']} " for ds in datasets])
    system_prompt = "你是一位笔记本厂商的数据分析专家，根据用户问题选择最匹配的数据集名称。只返回一个名称，不需要其他解释。"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"问题是：{question}\n\n可选 datasets:\n{descriptions}"},
    ]
    completion =  client.beta.chat.completions.parse(
        model=model,
        messages= messages,
        response_format=OutPutDsInfo
    )
    answer = completion.choices[0].message.parsed
    return answer.dataset_id, answer.dataset_name, answer.dataset_description
