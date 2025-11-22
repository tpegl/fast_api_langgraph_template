import logging

from langchain_core.runnables import RunnableConfig

from app.graphs.cv_parser.state import CVParserState
from app.graphs.utils import create_model


logger = logging.getLogger(__name__)


extra_invoke_conf = {"callbacks": []}


async def validate_input(state: CVParserState):
    validation_errors: list[str] = []
    new_state = None

    job_description = state.get("job_description", None)
    cv = state.get("cv", None)

    if not job_description:
        validation_errors.append("No input job_description found")
        logger.debug("No input job_description found. Likely an error")
        new_state = state.copy()
        new_state["validation_errors"].append(*validation_errors)
    else:
        logger.debug(f"JD = {job_description}")

    if not cv:
        validation_errors.append("No input cv found")
        logger.debug("No input cv found. Likely an error")
        new_state = state.copy()
        new_state["validation_errors"].append(*validation_errors)

    if new_state:
        return new_state

    return state


async def handle_failures(state: CVParserState):
    errors_report = {
        "validation_errors": state.get("validation_errors", []),
    }

    logger.debug(f"Validation errors found: {len(errors_report['validation_errors'])}")
    for validation_error in errors_report["validation_errors"]:
        logger.debug(validation_error)

    return state


async def parse_document(state: CVParserState):
    try:
        model = await create_model("parse-cv-and-grade")
        conf = RunnableConfig(callbacks=extra_invoke_conf["callbacks"], configurable={})

        logger.debug("Asking LLM if the provided CV is appropriate for the supplied JD")

        response = await model.ainvoke(
            {"job_description": state["job_description"], "cv": state["cv"]},
            config=conf,
        )

        response_content = (
            response.content if hasattr(response, "content") else str(response)
        )

        new_state = state.copy()
        new_state["extracted_response"] = response_content
        new_state["current_step"] = "parsing_completed"
        return new_state
    except Exception as e:
        error_str = f"Failed to parse document due to {e}"
        logger.error(error_str)

        new_state = state.copy()
        new_state["validation_errors"].append(error_str)
        return new_state


def finalise_processing(state: CVParserState):
    # TODO: any checks on the state that are deemed necessary after a cursory run
    return state
