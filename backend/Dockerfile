# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies (needed for compiling some packages if necessary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy processed dataset
COPY data/processed/restaurants.parquet /app/data/processed/restaurants.parquet

# Copy backend application code
COPY backend/src /app/backend/src

# Set working directory to backend for executing uvicorn
WORKDIR /app/backend

# Expose port and run the service
EXPOSE 8000
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT}"]
