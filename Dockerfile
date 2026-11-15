FROM python:3.12-slim

ARG EXTRAS="mcp,postgres,mysql"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DB_URL="sqlite:////data/nexprice.db"

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip install ".[${EXTRAS}]" && \
    useradd --create-home --shell /bin/bash nexprice && \
    mkdir -p /data && \
    chown -R nexprice:nexprice /app /data

USER nexprice
VOLUME ["/data"]

ENTRYPOINT ["nexprice"]
CMD ["--help"]
