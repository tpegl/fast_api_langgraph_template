import logging
import os

from dotenv import load_dotenv
from fastapi import HTTPException
from langgraph_sdk import get_client
from langgraph_sdk.client import LangGraphClient
from langgraph_sdk.schema import Assistant

logger = logging.getLogger(__name__)
load_dotenv()


class LanggraphManager:
    def __init__(self):
        self.client: LangGraphClient | None = None
        self.assistants: dict[str, Assistant] = {}

    def connect(self):
        try:
            self.client = get_client(
                url=os.getenv("LANGGRAPH_URL", None),
                api_key=os.getenv("LANGGRAPH_API_KEY", None),
            )
        except Exception as e:
            logger.error(f"Failed to connect to langgraph: {e}")
            raise

    async def get_assistant(self, graph_id: str):
        if not self.client:
            raise HTTPException(503, f"No assistant found for graph: {graph_id}")

        if graph_id in self.assistants:
            return self.assistants[graph_id]

        try:
            assistants = await self.client.assistants.search(graph_id=graph_id)
            if not assistants:
                raise ValueError(f"No assistants found with ID: {graph_id}")

            self.assistants[graph_id] = assistants[0]
            return self.assistants[graph_id]

        except Exception as e:
            logger.error(f"Failed to load assistant for graph {graph_id}: {e}")
            raise HTTPException(
                503, f"Failed to laod assistant for graph {graph_id}: {e}"
            )

    def get_client(self):
        if not self.client:
            raise HTTPException(503, "Agent was not initialised")

        return self.client

    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None
            self.assistants.clear()
            logger.info("Langgraph connection closed")


langgraph_manager = LanggraphManager()


def get_langgraph_client():
    return langgraph_manager.get_client()


async def get_langgraph_assistant(graph_id: str = "cv_parser"):
    return await langgraph_manager.get_assistant(graph_id=graph_id)
