import os
from dotenv import load_dotenv
from langsmith.async_client import AsyncClient

load_dotenv()

async def create_model(name: str, include_model: bool = True):
    client = AsyncClient(api_key=os.getenv("LANGGRAPH_API_KEY"))
    llm = await client.pull_prompt(name, include_model=include_model)
    return llm