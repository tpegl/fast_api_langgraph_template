import os
from dotenv import load_dotenv
from fastapi import FastAPI

from app.schemas.snake import SnakeModel

from app.routers.parse_cv import router as parse_cv_router

load_dotenv()

debug = os.getenv("DEBUG", "False") != "False"

app = FastAPI(
    title="Test FastAPI LangGraph Applicatio",
    debug=debug,
    openapi_url="/openapi.json" if debug else None
)

app.include_router(router=parse_cv_router)

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
        scientific_name="Natrix Natrix"
    )