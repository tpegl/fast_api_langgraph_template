from enum import Enum
from pydantic import BaseModel, Field

class ProcessingStatus(Enum):
    PENDING     = "pending"
    RUNNING     = "running"
    COMPLETED   = "completed"
    FAILED      = "failed"
    INTERRUPTED = "interrupted"

class ParseCVInitResponse(BaseModel):
    thread_id: str | None = Field(None)

class ParseCVOutcomeResponse(BaseModel):
    outcome: str | None = Field(None)
    status: ProcessingStatus = Field(ProcessingStatus.PENDING)
    errors: list[str] | None = Field(default_factory=list)