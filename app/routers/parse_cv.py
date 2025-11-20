import logging

import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from langgraph_sdk.client import LangGraphClient
from langgraph_sdk.schema import Assistant

from app.core.langgraph import get_langgraph_assistant, get_langgraph_client
from app.core.security import sanitise_filename, validate_file_upload

router = APIRouter(prefix="/parse", tags=["parse"])
logger = logging.getLogger(__name__)

LanggraphClientDep = Annotated[LangGraphClient, Depends(get_langgraph_client)]
AssistantDep = Annotated[Assistant, Depends(get_langgraph_assistant)]

@router.post("/")
async def parse_cv(
    files: list[UploadFile],
    client: LanggraphClientDep,
    assistant: AssistantDep
):
    # We only want to process 1 file
    file = files[0]
    tmp_file_path: str | None = None

    is_valid, error_message = validate_file_upload(
        filename=file.filename or "unknown",
        content_type=file.content_type,
        max_size=50 * 1024 * 1024
    )

    if not is_valid:
        return HTTPException(
            status_code=400,
            detail=error_message
        )

    try:
        safe_filename = sanitise_filename(file.filename or "upload")

        async with aiofiles.tempfile.NamedTemporaryFile(
            "wb+", suffix=f"_{safe_filename}", delete=False
        ) as tmp_file:
            max_file_size = 50 * 1024 * 1024
            content = await file.read()

            if len(content) > max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds maximum allowed size of {max_file_size // (1024 * 1024)}MB"
                )

            _ = await tmp_file.write(content)
            tmp_file_path = tmp_file.name

        file_size = os.path.getsize(tmp_file_path)

        file.filename.lower().split(".")[-1] if file.filename else ""
        # TODO: file to markdown parsers
        # markdown_content = 

    except Exception as e:
        logger.error(e)