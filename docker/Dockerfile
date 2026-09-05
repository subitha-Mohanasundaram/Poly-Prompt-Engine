FROM python:3.11-slim as builder

WORKDIR /install

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim as runtime

LABEL maintainer="Poly Prompt Engine Team"
LABEL version="1.0"
LABEL description="FastAPI-based question variation generation system"

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
