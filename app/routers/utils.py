import json
import logging

logger = logging.getLogger(__name__)


PARSE_CV_PROMPT = """Here is the candidates CV. Please extract all relevant information and return it in easy to understand language while highlighting relevant information based on the job description that this CV is meant to be for.

Below is the Job Description:
{job_description}

And the CV is a file that has been attached. Parse it and do not leave out any relevant information. If there is any missing information that you'd expect, flag it. DO NOT MAKE UP ANY INFORMATION THAT IS NOT PRESENT."""

MARKDOWN_CODE_BLOCK_QUOTES = "```"
MARKDOWN_JSON_BLOCK_START = MARKDOWN_CODE_BLOCK_QUOTES + "json"

def extract_agent_text(agent_response: dict[str, str] | list[str] | str) -> str:
        """
        Extract text content from various agent response types.
        """
        # Handle smolagents AgentText type
        if hasattr(agent_response, "text"):
            text = agent_response["text"]  # pyright: ignore[reportCallIssue, reportArgumentType]
        elif hasattr(agent_response, "content"):
            text = agent_response["content"]  # pyright: ignore[reportCallIssue, reportArgumentType]
        elif isinstance(agent_response, str):
            text = agent_response
        elif isinstance(agent_response, list):
            text = json.dumps(agent_response)
        else:
            # Fallback: convert to string
            text = str(agent_response)

        # Remove <think> tags and their content
        import re

        # Pattern to match <think> tags and everything between them
        think_pattern = r"<think>.*?</think>"
        # Remove all occurrences, including nested ones
        cleaned_text = re.sub(think_pattern, "", text, flags=re.DOTALL)

        # Also handle cases where tags might not be properly closed
        # Remove any remaining <think> opening tags
        cleaned_text = re.sub(r"<think>.*", "", cleaned_text, flags=re.DOTALL)

        # Clean up any extra whitespace left behind
        cleaned_text = cleaned_text.strip()

        # Extract content from markdown code blocks if present
        if MARKDOWN_CODE_BLOCK_QUOTES in cleaned_text:
            # Pattern to match markdown code blocks (with or without language specifier)
            # Note: This pattern could be vulnerable to ReDoS with malicious input
            # We mitigate by limiting input size and using regex timeout (Python 3.11+)
            code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"

            # Limit input size to prevent worst-case scenarios
            if len(cleaned_text) > 100000:  # 100KB limit
                # For very large inputs, use a simpler approach
                if MARKDOWN_JSON_BLOCK_START in cleaned_text:
                    start = cleaned_text.find(MARKDOWN_JSON_BLOCK_START) + 8
                    end = cleaned_text.find(MARKDOWN_CODE_BLOCK_QUOTES, start)
                    if end > start:
                        cleaned_text = cleaned_text[start:end].strip()
                elif MARKDOWN_CODE_BLOCK_QUOTES in cleaned_text:
                    start = cleaned_text.find(MARKDOWN_CODE_BLOCK_QUOTES) + 3
                    end = cleaned_text.find(MARKDOWN_CODE_BLOCK_QUOTES, start)
                    if end > start:
                        cleaned_text = cleaned_text[start:end].strip()
            else:
                try:
                    # For Python 3.11+, we could use: re.findall(pattern, text, timeout=1.0)
                    # For now, we use the existing regex with size limits
                    matches = re.findall(code_block_pattern, cleaned_text, re.DOTALL)
                    if matches:
                        # If we found code blocks, extract and join their contents
                        extracted_content = "\n".join(matches)
                        cleaned_text = extracted_content.strip()
                except Exception as e:
                    logger.error(e)

        return cleaned_text