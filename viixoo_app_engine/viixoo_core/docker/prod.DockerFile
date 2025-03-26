FROM python:3.12.3

ARG PYTHON_VERSION=3.12.3
ARG PYTHON_SHORT_VER=3.12.3


ENV PYTHONUNBUFFERED=1

WORKDIR /viixoo_core/

ENV UV_LINK_MODE=copy

ENV PYTHONPATH=/viixoo_core

COPY ./pyproject.toml /viixoo_core/

COPY ./viixoo_core /viixoo_core/app


COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

EXPOSE 8000

