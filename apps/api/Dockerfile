FROM python:3.11-slim

ARG INSTALL_LAYA=false
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
RUN pip install --no-cache-dir . && if [ "$INSTALL_LAYA" = "true" ]; then pip install --no-cache-dir ".[laya]"; fi

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn escalate.main:app --host 0.0.0.0 --port 8000"]

