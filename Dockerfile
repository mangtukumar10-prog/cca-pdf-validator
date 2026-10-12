# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies (build tools and certs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency specifications first for layer caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and root certificates
COPY roots/ ./roots/
COPY static/ ./static/
COPY main.py validator.py pdf_stamper.py sync_cca_roots.py ./
COPY *.pdf ./

# Expose standard port
EXPOSE 8000

# Run FastAPI with uvicorn listening on all interfaces
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
