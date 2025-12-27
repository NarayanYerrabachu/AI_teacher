# Backend Dockerfile for AI Teacher
# Multi-stage build for optimized image size

FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pipenv (suppress root warning in Docker)
RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install pipenv --root-user-action=ignore

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies to system (not virtualenv) for cleaner image
# Install PyTorch CPU-only version first for smaller size and faster download
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu --root-user-action=ignore

# Install remaining dependencies from Pipfile.lock
RUN pipenv install --system --deploy --ignore-pipfile

# Production stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy backend application code to /app directory
COPY backend/ /app/

# Create directories for uploads, chroma_db, and logs
RUN mkdir -p /app/uploads /app/chroma_db /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Keep working directory as /app
# Set Python path to parent for module imports
ENV PYTHONPATH=/.

# Run the application - the app directory will be found via PYTHONPATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/"]
