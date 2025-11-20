# Super simple FastAPI project bootstrap

Set up a FastAPI project using [UV](https://github.com/astral-sh/uv) and Docker

## How to use

- Clone, copy, get these files into a place
- Using Docker/Podman:
    - `docker build --tag fastapibootstrap:latest .`
    - `docker run -p 8000:8080 fastapibootstrap:latest`
- Just run it:
    - `uv sync --locked --no-dev --no-editable`
    - `fastapi run app/main.py`