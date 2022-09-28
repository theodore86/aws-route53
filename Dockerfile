FROM ubuntu:22.04 AS base

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    python3-setuptools \
    python3-pip \
    python3-dev && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

FROM base as run

WORKDIR /app

COPY src/ /app/src
COPY record_cleanup.py /app/
COPY requirements.txt /app/

RUN python3 -m pip install --no-cache-dir -r requirements.txt && \
    chmod +x /app/record_cleanup.py && \
    useradd -ms /bin/bash ubuntu

USER ubuntu

ENTRYPOINT ["python3", "record_cleanup.py"]
