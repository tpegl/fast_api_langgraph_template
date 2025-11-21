import logging

from app.graphs.cv_parser.state import CVParserState


logger = logging.getLogger(__name__)


async def validate_input(state: CVParserState):
    validation_errors: list[str] = []

    messages = state.get("messages", [])

    if not messages:
        validation_errors.append("No input messages found")
        logger.error("No input messages found. Likely an error or called too early.")
        new_state = state.copy()
        new_state["validation_errors"].append(*validation_errors)
        return new_state
    else:
        logger.debug(f"Messages types: {[type(msg).__name__ for msg in messages]}")

    return state


async def handle_failures(state: CVParserState):
    errors_report = {
        "validation_errors": state.get("validation_errors", []),
    }

    logger.error(f"Validation errors found: {len(errors_report['validation_errors'])}")
    for validation_error in errors_report["validation_errors"]:
        logger.error(validation_error)

    return state
