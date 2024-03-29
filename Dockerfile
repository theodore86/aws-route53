# syntax = docker/dockerfile:1.3
FROM python:3.11.5-slim AS build

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Requirements in separate stage
FROM build as build-env

WORKDIR /

COPY ./requirements.txt ./

# Buildkits caching
RUN --mount=type=cache,target=/root/.cache/ \
      python3 -m pip install \
      --no-compile \
      --disable-pip-version-check \
      -r requirements.txt

FROM python:3.11.5-slim AS run

COPY --from=build-env /opt/venv /opt/venv

WORKDIR /app

COPY src/ ./src
COPY record_cleanup.py ./

RUN chmod +x "/app/record_cleanup.py" && \
    useradd -ms /bin/bash ubuntu

USER ubuntu

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python3", "record_cleanup.py"]
