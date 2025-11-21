import logging

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from app.graphs.cv_parser.state import CVParserState
from app.graphs.utils import create_model


logger = logging.getLogger(__name__)


extra_invoke_conf = {"callbacks": []}


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

async def parse_document(state: CVParserState):
    try:
        model = await create_model("parse-cv-and-grade")
        conf = RunnableConfig(
            callbacks=extra_invoke_conf["callbacks"],
            configurable={}
        )
        messages = state["messages"]

        for msg in messages:
            if isinstance(msg, HumanMessage | dict):
                msg_content = msg.get("content", "") if isinstance(msg, dict) else msg.content

                preview = (
                    str(msg_content)[:500] + "..." if len(str(msg_content)) > 500 else str(msg_content)
                )
                logger.debug(f"Sending to LLM (preview): {preview}")
                break

        response = await model.ainvoke(messages, config=conf)

        response_content = response.content if hasattr(response, "content") else str(response)

        new_state = state.copy()
        new_state["messages"] = [response]
        new_state["extracted_response"] = response_content
        new_state["current_step"] = "parsing_completed"
        return new_state
    except Exception as e:
        logger.error(e)
    return state

def finalise_processing(state: CVParserState):
    # TODO: any checks on the state that are deemed necessary after a cursory run
    return state