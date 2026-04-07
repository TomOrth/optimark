# syntax=docker/dockerfile:1

FROM dhi.io/python:3.13-alpine3.23 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON=/usr/bin/python

WORKDIR /app/backend

COPY --from=ghcr.io/astral-sh/uv:0.10.12 /uv /uvx /usr/local/bin/

COPY --chown=65532:65532 backend/ ./

RUN ["uv", "sync", "--all-packages", "--frozen", "--no-dev", "--python", "/usr/bin/python"]

ENV PATH="/app/backend/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "optimark_athena.app:app", "--host", "0.0.0.0", "--port", "8000"]
