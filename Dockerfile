FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    python3-setuptools \
    python3-pip \
    python3-dev && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

WORKDIR /app

COPY src/ ./src
COPY record_cleanup.py requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt && \
    chmod +x /app/record_cleanup.py && \
    useradd -ms /bin/bash ubuntu

USER ubuntu

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python3", "record_cleanup.py"]
