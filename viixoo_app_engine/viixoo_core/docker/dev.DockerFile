FROM python:3.10.11

ARG PYTHON_VERSION=3.10.11
ARG PYTHON_SHORT_VER=3.10.11

ENV PYTHONPATH="/viixoo_app_engine"

WORKDIR "${PYTHONPATH}"

ENV PYTHONUNBUFFERED=1

COPY ./viixoo_core/ "${PYTHONPATH}/viixoo_core/"
COPY ./viixoo_backend_apps/ "${PYTHONPATH}/viixoo_backend_apps/"

RUN cd /viixoo_app_engine/viixoo_core/ && \
    pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements-dev.txt

RUN cd /viixoo_app_engine/viixoo_backend_apps/mrp/ && pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8002
