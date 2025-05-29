from openai import AzureOpenAI
from dg_pbi_agents.schemas.base import ValidationResult, ExecutionResult
import os


class ResultValidator:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    async def validate(self, result: ExecutionResult, context: dict) -> ValidationResult:
        prompt = f"""验证查询结果合理性：

        原始问题：{context['question']}
        DAX表达式：{context['dax_expression']}
        执行结果：{result.json()}

        检查点：
        1. 结果是否符合预期逻辑
        2. 数据量级是否合理
        3. 是否有异常值"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return ValidationResult.parse_raw(response.choices[0].message.content)