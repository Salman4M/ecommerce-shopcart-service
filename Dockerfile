FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install uv && uv sync --frozen

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Copy all application code
COPY src/ /app/src

ENV PYTHONPATH=/app/src

EXPOSE 8000


# Default command to run fastapi  server
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--proxy-headers"]