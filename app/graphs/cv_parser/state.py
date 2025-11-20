import operator
from typing import Annotated, TypedDict

from langchain.messages import AnyMessage

class CVParserState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    current_step: str
    validation_errors: list[str]
    extracted_skills: list[dict[str, str]]
    extracted_experience: list[dict[str, str]]
    extracted_summary: str