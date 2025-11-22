from langsmith.async_client import AsyncClient

from app.core.settings import get_settings

settings = get_settings()


async def create_model(name: str, include_model: bool = True):
    client = AsyncClient(api_key=settings.langsmith_api_key)
    llm = await client.pull_prompt(name, include_model=include_model)
    return llm
