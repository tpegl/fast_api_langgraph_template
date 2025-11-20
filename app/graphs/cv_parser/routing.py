import logging

from app.graphs.cv_parser.state import CVParserState

logger = logging.getLogger(__name__)

def route_after_validation(state: CVParserState):
    current_step = state.get("current_step")
    validation_errors = state.get("validation_errors", [])

    if current_step == "validation_failed":
        return "handle_failure"

    return "parse_document"