from fastapi import FastAPI

from app.schemas.snake import SnakeModel

app = FastAPI()

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