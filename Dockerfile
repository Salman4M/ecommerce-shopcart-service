FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY src/pyproject.toml src/uv.lock ./

# Install Python dependencies
RUN pip install uv && uv sync --frozen

# Copy all application code
COPY src/ /app

ENV PYTHONPATH=/app

# Default command to run Django dev server
CMD ["uv", "run","uvicorn" ,"python", "manage.py", "runserver", "0.0.0.0:8000"]
