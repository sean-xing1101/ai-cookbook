from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

client = AsyncAzureOpenAI(
    azure_endpoint='https://kagegpt.openai.azure.com/',
    api_version='2024-08-01-preview',
    api_key='65ae5a69eccf4684bd23812648d1ccb7',
)

model = OpenAIModel(
    'gpt-4o',
    provider=OpenAIProvider(openai_client=client),
)
agent = Agent(model)

result = agent.run_sync('how to play football?')
print(result.output)


