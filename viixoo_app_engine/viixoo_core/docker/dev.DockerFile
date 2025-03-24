FROM python:3.12.3

ARG PYTHON_VERSION=3.12.3
ARG PYTHON_SHORT_VER=3.12.3


ENV PYTHONUNBUFFERED=1

WORKDIR /viixoo_core/

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV PATH="/viixoo_core/.venv/bin:$PATH"

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

ENV PYTHONPATH=/viixoo_core

COPY ./pyproject.toml /viixoo_core/

COPY ./viixoo_core /viixoo_core/app


COPY requirements-dev.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements-dev.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

EXPOSE 8002
