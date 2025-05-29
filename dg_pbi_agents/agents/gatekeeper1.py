# from multiprocessing.connection import answer_challenge
#
# from openai import OpenAI,AzureOpenAI
# import os
# from dotenv import load_dotenv
# from pydantic import BaseModel
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
# class CheckIfBusinessEvent(BaseModel):
#     if_business: bool
#     confidence: float
#     reason: str
#
# def check_if_business_question(question: str):
#     system_prompt = "你是一个笔记本厂商分类判断助手，请判断以下内容是否为业务相关问题。返回是否是业务问题和一个0到1之间的置信度评分。给出我判断原因,用中文表示"
#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": question},
#     ]
#     completion =  client.beta.chat.completions.parse(
#         model=model,
#         messages=messages,
#         response_format=CheckIfBusinessEvent
#     )
#     answer = completion.choices[0].message.parsed
#     return answer.if_business, answer.confidence, answer.reason
#
# question= '我想查看一下在nova平台近两天测试了多少case'
# question2 = '我想看一下今天的天气'
# completion = check_if_business_question(question)

# agents/gatekeeper.py
from openai import AzureOpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Tuple
from dg_pbi_agents.schemas.base import BusinessCheckResult
import asyncio
load_dotenv()


class BusinessClassifier:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        )
        self.model = "gpt-4o"
        # self.system_prompt = """你是一个专注于电脑产品的业务问题分类助手。用户的问题可能涉及但不限于以下内容：
        # 1. 产品测试结果（如测试了多少case、测试通过率等）
        # 2. 硬件信息（如 CPU、内存、主板等）
        # 3. 软件配置（如操作系统版本、驱动程序版本等）
        # 4. 测试中出现的问题（如 bug、crash、异常指标等）
        # 5. 问题跟踪（如 P1 的 issue、bug 数量等）
        #
        # 请根据用户的问题内容，判断其是否属于业务相关的问题，并返回：
        # 1. `是否为业务问题`（布尔值 true/false）
        # 2. `置信度`（0 到 1 之间的浮点数，表示你对此判断的信心）
        # 3. `判断原因`（简要说明你为何作出这样的判断）
        #
        # 注意：不要过度泛化，仅当问题明显与业务范畴无关时才应判断为非业务问题。"""
        self.system_prompt = """You are an expert in classifying business-related questions about computer products. User questions may cover, but are not limited to, the following topics:
        1. Test results (e.g., number of test cases run, pass rate)
        2. Hardware information (e.g., CPU, memory, motherboard)
        3. Software configuration (e.g., operating system version, driver versions)
        4. Issues encountered during testing (e.g., bugs, crashes, abnormal metrics)
        5. Issue tracking (e.g., number of P1 issues, bug counts)

        Please determine whether the user's question is business-related and return:
        1. `Is it a business-related question?` (Boolean value true/false)
        2. `Confidence level` (A float between 0 and 1, indicating your confidence in this judgment)
        3. `Reason for judgment` (A brief explanation of why you made this judgment)

        Note: Do not over-generalize. Only classify a question as non-business-related if it is clearly outside the scope of business. If the question is ambiguous but could potentially be related to business, it should be classified as business-related.answer in Chinese"""

    async def check(self, question: str) -> BusinessCheckResult:
        """检查问题是否属于业务范畴"""
        messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question},
            ]
        completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=messages,
                    response_format=BusinessCheckResult
                )
        answer = completion.choices[0].message.parsed
        return answer





# 示例问题
sample_questions = [
    "今天测试了多少case？",
    "请问距离高考还有几天",
    "近两天出现了在Byamax14上出现了多少bug",
    "P1的issue今天开了多少笔",
    "今天天气怎么样？",  # 非业务问题
    "我想查看端到端测试的详情",
    "我想查看一下在2025-05-20那天开的obs还有多少没有被关闭",
    "笔记本屏幕坏了,该怎么处理",
    "我想看一下Byamax14的详细情况"]

async def test_business_classifier():
    # 创建 BusinessClassifier 实例
    classifier = BusinessClassifier()

    # 创建一个任务列表
    tasks = [classifier.check(question) for question in sample_questions]

    # 并行执行所有任务
    results = await asyncio.gather(*tasks)
    a=1
    # 打印每个问题的测试结果
    for question, result in zip(sample_questions, results):
        print(f"测试问题: {question}")
        print(f"结果: {result}")
        print("-" * 40)

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_business_classifier())