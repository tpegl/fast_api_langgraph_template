from pydantic import BaseModel, Field

class SnakeModel(BaseModel):
    colour: str | None = Field()
    length: float | None = Field(0.0)
    length_unit: str = Field("cm")
    name: str | None = Field()
    scientific_name: str | None = Field()