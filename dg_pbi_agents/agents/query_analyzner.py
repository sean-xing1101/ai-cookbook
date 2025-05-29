from openai import AzureOpenAI
from dg_pbi_agents.schemas.base import QueryPlan, DatasetMetadata
import os


class QueryAnalyzer:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    async def analyze(self, question: str, metadata: DatasetMetadata) -> QueryPlan:
        prompt = f"""分析用户问题并生成查询计划：

        用户问题：{question}

        可用元数据：
        {metadata.json(indent=2)}

        输出要求：
        - 识别需要查询的表（至少一个）
        - 列出涉及的字段
        - 提取过滤条件
        - 需要时指定表连接方式"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return QueryPlan.parse_raw(response.choices[0].message.content)