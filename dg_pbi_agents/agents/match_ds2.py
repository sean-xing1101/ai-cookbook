# from openai import OpenAI,AzureOpenAI
# import os
# from dotenv import load_dotenv
# from pydantic import BaseModel
# from dg_pbi_agents.config.donfig_info import datasets
# load_dotenv()
#
# #azure openai
# client = AzureOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
# )
# model="gpt-4o"
#
# datasets_info = datasets
#
# class OutPutDsInfo(BaseModel):
#     dataset_id: str
#     dataset_name: str
#     dataset_description: str
#
# def select_dataset(question: str) -> tuple[bool, float]:
#     descriptions = "\n".join([f"{ds['name']}: {ds['desc']} id:{ds['id']} " for ds in datasets])
#     system_prompt = "你是一位笔记本厂商的数据分析专家，根据用户问题选择最匹配的数据集名称。只返回一个名称，不需要其他解释。"
#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": f"问题是：{question}\n\n可选 datasets:\n{descriptions}"},
#     ]
#     completion =  client.beta.chat.completions.parse(
#         model=model,
#         messages= messages,
#         response_format=OutPutDsInfo
#     )
#     answer = completion.choices[0].message.parsed
#     return answer.dataset_id, answer.dataset_name, answer.dataset_description


# agents/dataset_matcher.py
from openai import AzureOpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import List
from dg_pbi_agents.schemas.base import DatasetInfo
from dg_pbi_agents.config.donfig_info import datasets  # 假设数据集配置已迁移
import asyncio
load_dotenv()


class DatasetMatcher:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        )
        self.model = "gpt-4o"
        self.datasets = datasets
        self.system_prompt = """
        您是一位严格的数据目录专家，必须根据用户问题从以下数据集列表中选择最相关的一个数据集。选择时必须遵守以下规则：

        1. 只能从提供的固定数据集列表中选择，禁止创建或想象任何不存在的数据集
        2. 如果问题与任何数据集都不匹配，返回空值
        3. 必须严格使用指定的JSON格式输出
        4. 置信度评分必须基于问题与数据集描述的实际匹配程度

        可用数据集列表：
        {datasets_list}

        输出要求：
        - 严格使用以下JSON结构:{{"dataset_id": "数据集id值", "dataset_name": "数据集名称", "dataset_description": "数据集描述", "response": "模型的回答"}}
        - dataset_id必须是下面列表中的有效ID
        - 如果没有匹配数据集，返回：{{"dataset_id": "", "dataset_name": "", "dataset_description": "", "response": "模型的回答"}}
        """

    def _format_datasets(self) -> str:
        return "\n".join(
            [f"ID: {ds['id']} | 名称: {ds['name']} | 描述: {ds['desc']}"
            for ds in self.datasets]
        )

    async def match(self, question: str) -> DatasetInfo:
        """匹配最相关数据集"""
        descriptions = self._format_datasets()
        # 使用格式化后的提示词
        formatted_system_prompt = self.system_prompt.format(datasets_list=descriptions)
        messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": f"问题是：{question}"},
        ]
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=DatasetInfo
        )
        answer = completion.choices[0].message.parsed

        # 修复未匹配数据集时的输出问题
        if not answer.dataset_id:
            answer.response = completion.choices[0].message.content

        return answer





# 示例问题
sample_questions = [
    "今天测试了多少case？",
    "我想查看baymax14有哪些component",
    "近两天在Byamax14上出现了多少bug",
    "P1的issue今天开了多少笔",
    "过去三个月case执行的趋势？",  # 非业务问题
    "我想查看端到端测试的详情",
    "我想查看一下在2025-05-20那天开的obs还有多少没有被关闭"
]

async def test_dataset_matcher():
    # 创建 DatasetMatcher 实例
    matcher = DatasetMatcher()

    # 创建一个任务列表
    tasks = [matcher.match(question) for question in sample_questions]

    # 并行执行所有任务
    results = await asyncio.gather(*tasks)
    a=1
    # 打印每个问题的测试结果
    for question, result in zip(sample_questions, results):
        print(f"测试问题: {question}")
        print(f"匹配的数据集 ID: {result[0]}")
        print(f"匹配的数据集名称: {result[1]}")
        print(f"匹配的数据集描述: {result[2]}")
        print("-" * 40)

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_dataset_matcher())
