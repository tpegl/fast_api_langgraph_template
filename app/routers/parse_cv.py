import base64
import logging


from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from langgraph_sdk.client import LangGraphClient
from langgraph_sdk.schema import Assistant

from app.core.langgraph import get_langgraph_assistant, get_langgraph_client
from app.core.security import validate_file_upload
from app.routers.utils import extract_agent_text
from app.schemas.parse_cv import (
    ParseCVInitResponse,
    ParseCVOutcomeResponse,
    ProcessingStatus,
)

router = APIRouter(prefix="/parse", tags=["parse"])
logger = logging.getLogger(__name__)

LanggraphClientDep = Annotated[LangGraphClient, Depends(get_langgraph_client)]
AssistantDep = Annotated[Assistant, Depends(get_langgraph_assistant)]


@router.post("/")
async def parse_cv(
    file: UploadFile, client: LanggraphClientDep, assistant: AssistantDep
):
    # Attempt to parse a CV and see if it is appropriate for a supplied job description

    file_contents = None

    is_valid, error_message = validate_file_upload(
        filename=file.filename or "unknown",
        content_type=file.content_type,
        max_size=50 * 1024 * 1024,
    )

    if not is_valid:
        return HTTPException(status_code=400, detail=error_message)

    try:
        max_file_size = 50 * 1024 * 1024
        content = await file.read()

        if len(content) > max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {max_file_size // (1024 * 1024)}MB",
            )

        file_contents = base64.b64encode(content).decode()

        thread = await client.threads.create()

        # input becomes the `state`` of the graph. So we populate it here as we aren't
        # explicitly creating any of these values in our graph but you CAN do that to
        # avoid having to make the input so large.
        input = {
            "job_description": "Senior Python Engineer. ",
            "cv": f"data:{file.content_type};base64,{file_contents}",
            "current_step": None,
            "validation_errors": [],
            "extracted_response": None,
        }

        _ = await client.runs.create(
            thread["thread_id"], assistant["assistant_id"], input=input
        )

        return ParseCVInitResponse(thread_id=thread["thread_id"])

    except Exception as e:
        logger.error(e)
        return ParseCVInitResponse(thread_id=None)


@router.get("/status/{thread_id}/", response_model=ParseCVOutcomeResponse)
async def get_status(thread_id: str, client: LanggraphClientDep):
    # This API is for checking the status of a running LLM call. It takes the thread_id that was returned
    # from the above parse_cv call and checks in on the status of the thread in LangGraph
    thread_errors: list[str] = []

    try:
        max_attempts = 30
        for _ in range(max_attempts):
            thread_state = await client.threads.get_state(thread_id)

            runs = await client.runs.list(thread_id)
            if runs:
                latest_run = runs[0] if isinstance(runs, list) else runs

                run_id = latest_run.get("run_id") or latest_run.get("id")
                run_status = latest_run.get("status", "unknown")

                logger.info(f"Latest run status: {run_status}, run_id: {run_id}")

                if run_status in ["pending", "running", "active"]:
                    return ParseCVOutcomeResponse(
                        outcome="Processing in progress",
                        status=ProcessingStatus.RUNNING,
                        errors=thread_errors,
                    )

                if run_status in ["error", "failed"]:
                    error_msg = latest_run.get("error") or "Run failed"
                    thread_errors.append(error_msg)
                    return ParseCVOutcomeResponse(
                        outcome=error_msg,
                        status=ProcessingStatus.FAILED,
                        errors=thread_errors,
                    )

            if thread_state and thread_state.get("values"):
                state_values = thread_state["values"]

                logger.info(state_values)

                if (
                    isinstance(state_values, dict)
                    and "extracted_response" in state_values
                ):
                    if "validation_errors" in state_values and isinstance(
                        state_values["validation_errors"], list
                    ):
                        thread_errors.append(*state_values["validation_errors"])

                    response: str = state_values["extracted_response"]

                    if response and len(response) > 1:
                        response = extract_agent_text(response)

                        logger.info(f"Got response from agent: {response}")

                        return ParseCVOutcomeResponse(
                            outcome=response,
                            status=ProcessingStatus.COMPLETED,
                            errors=[],
                        )
                    else:
                        logger.info(f"Agent response was empty: {response}")

        return ParseCVOutcomeResponse(
            outcome="Failed to parse CV. Check logs",
            status=ProcessingStatus.FAILED,
            errors=thread_errors,
        )

    except Exception as e:
        error_msg = f"Failed to parse CV with agent: {e}"
        logger.error(error_msg)
        thread_errors.append(error_msg)
        return ParseCVOutcomeResponse(
            outcome=error_msg, status=ProcessingStatus.FAILED, errors=thread_errors
        )
