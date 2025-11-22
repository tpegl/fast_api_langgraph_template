from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.settings import get_settings
from app.schemas.snake import SnakeModel

from app.routers.parse_cv import router as parse_cv_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Test database connection and initialize LangGraph on startup."""

    from app.core.langgraph import langgraph_manager

    # Initialize LangGraph connection
    try:
        print("CONNECTING TO LANGGRAPH")
        langgraph_manager.connect()
        print("LangGraph connection successful")
    except Exception as e:
        print(f"LangGraph connection failed: {e}")
        # Continue startup even if LangGraph fails

    yield

    # Cleanup
    _ = langgraph_manager.close()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

app.include_router(router=parse_cv_router)


# Generic routes for testing purposes. Can easily be removed to leave only
# router based ones
@app.get("/")
def _() -> str:
    return "Hello, one and all!"


@app.get("/snake", response_model=SnakeModel)
def make_snake():
    return SnakeModel(
        colour="green",
        length=12.5,
        length_unit="cm",
        name="Grass Snake",
        scientific_name="Natrix Natrix",
    )
