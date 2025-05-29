from openai import AzureOpenAI
from dg_pbi_agents.schemas.base import DAXRequest, DAXResponse
import os


class DAXGenerator:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    async def generate(self, request: DAXRequest) -> DAXResponse:
        prompt = f"""根据以下信息生成DAX表达式：

        用户问题：{request.question}

        查询计划：
        {request.query_plan.json(indent=2)}

        要求：
        1. 使用标准DAX语法
        2. 添加注释说明
        3. 确保过滤条件正确"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return DAXResponse.parse_raw(response.choices[0].message.content)