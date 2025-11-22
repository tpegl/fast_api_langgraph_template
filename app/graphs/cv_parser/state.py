from typing import TypedDict


class CVParserState(TypedDict):
    job_description: str | None
    cv: str | None
    current_step: str
    validation_errors: list[str]
    extracted_response: str
