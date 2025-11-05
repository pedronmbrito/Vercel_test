FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Expose port
EXPOSE 3000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "2", "app:flask_app"]
