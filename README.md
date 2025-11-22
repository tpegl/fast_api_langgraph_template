# FastAPI LangGraph project template

Set up a FastAPI and LangGraph project using [UV](https://github.com/astral-sh/uv) and Docker

## How to use

- Clone, copy, get these files into a place
- Using Docker/Podman:
    - `docker build --tag fastapilanggraph:latest .`
    - `docker run -p 8000:8080 fastapilanggraph:latest`
- Just run it:
    - `uv sync --locked --no-dev --no-editable`
    - `fastapi run app/main.py`

### Using with LangSmith
- Install langgraph-cli (should be some flavour of `pip install langgraph-cli` but check the docs if you are unsure or use an annoying distro - **cough**Arch**cough**)
- Install all dependencies using `uv sync`
- Create your prompt in LangSmith using a model configuration (here's one I made earlier: https://eu.smith.langchain.com/hub/vapourisation/parse-cv-and-grade - it uses Google Gemini so you'll need to get an API key from aistudio.google.com) 
- Ensure you have some env vars set (depends on your LLM of choice but will be something like: `<PLATFORM_NAME>_API_KEY` i.e. `GOOGLE_API_KEY` or `OPENAI_API_KEY`) - these are used by the langgraph CLI when you attempt to call the model based on the parameters set in LangSmith
- With the local env active, start the langgraph CLI (hint: you may need to use the `--allow-blocking` flag when using Google Gemini models because the library has some blocking calls still in there somewhere)
- Start the actual app `fastapi run app/main.py`
- Call the API endpoint using your API interaction tool of choice with a `file`
    - At this point you should be able to see the langgraph cli begin processing the request
- All going well, get the `thread_id` from the response and call the status endpoint: `http://0.0.0.0:8000/parse/status/{thread_id}/` and you should see either a processing message or the actual response