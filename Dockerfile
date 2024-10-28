# Use a slim Python base image
FROM python:3.9-slim

# Set a working directory
WORKDIR /app

# Create a non-root user and group with a writable home directory
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser appuser

# Install system dependencies securely
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Ensure the home directory has correct permissions for appuser
RUN mkdir -p /home/appuser/.local && chown -R appuser:appuser /home/appuser

# Switch to non-root user
USER appuser

# Copy requirements.txt and install Python dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY --chown=appuser:appuser app/ ./app/

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
