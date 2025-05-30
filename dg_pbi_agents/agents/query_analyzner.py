from openai import AzureOpenAI
from dg_pbi_agents.schemas.base import QueryPlan, DatasetMetadata
import os
from dotenv import load_dotenv

load_dotenv()

class QueryAnalyzer:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        )
        self.model = "gpt-4o"
        self.system_prompt = """你是一个业务问题分析专家，分析用户问题并生成查询计划:
                                可用元数据：
                                {metadata}
                                输出要求
                                - 识别需要查询的表（至少一个）
                                - 列出涉及的字段
                                - 提取过滤条件
                                - 需要时指定表连接方式
                                """
    async def analyze(self, question: str, metadata: DatasetMetadata) -> QueryPlan:

        """分析用户问题并生成查询计划"""
        formatted_metadata = metadata.model_dump_json(indent=2)
        messages = [
                {"role": "system", "content": self.system_prompt.format(metadata=formatted_metadata)},
                {"role": "user", "content": f"问题是：{question}"},
            ]
        completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=QueryPlan
            )
        answer = completion.choices[0].message.parsed

        return answer