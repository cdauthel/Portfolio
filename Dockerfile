FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY packages.txt /tmp/packages.txt

RUN apt-get update \
    && xargs -a /tmp/packages.txt apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml README.md /app/
COPY src /app/src
COPY app /app/app
COPY scripts /app/scripts
COPY pipelines /app/pipelines
COPY docs /app/docs
COPY tests /app/tests

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
