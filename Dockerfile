FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker caching)
COPY requirements.txt .

# Install Python dependencies
# Include uvicorn[standard] to support WebSockets (includes websockets/wsproto)
RUN pip install --no-cache-dir "uvicorn[standard]" && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Collect static files (Django)
RUN python manage.py collectstatic --noinput

# Expose the app port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && gunicorn IhrHub.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"]
