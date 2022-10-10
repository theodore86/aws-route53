FROM python:3.10.7-slim AS build

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Re-execute this step only if dependencies changes
FROM build as build-env

COPY requirements.txt ./

RUN python3 -m pip install \
      --no-compile \
      --disable-pip-version-check \
      --no-cache-dir \
      -r requirements.txt

FROM python:3.10.7-slim AS run

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
