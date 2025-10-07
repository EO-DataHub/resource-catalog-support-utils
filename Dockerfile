# Use a smaller base image since we don't need build tools
FROM python:3.13-alpine

WORKDIR /app

# Install only essential runtime dependencies
RUN apk add --no-cache \
    && rm -rf /var/cache/apk/*

# Copy requirements and install Python packages
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app/ /app/app/
COPY ./lambda_handler.py /app/

# Expose port
EXPOSE 8000

# Set environment variables
ENV LOG_LEVEL=INFO
ENV LOG_REQUESTS=true
ENV LOG_REQUEST_BODY=false

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

