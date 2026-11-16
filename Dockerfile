# Dockerfile

FROM python:3-alpine

# Set working directory
WORKDIR /app

# Upgrade OS packages to pick up security fixes not yet in the base image
RUN apk upgrade --no-cache

# Install runtime dependencies
RUN pip install --no-cache-dir requests prometheus-client

# Copy the Python source file
COPY main.py /app/main.py

# Declare environment variables
ENV LLAMACPP_BASE_URL="http://localhost:8000"
ENV SERVER_PORT="8001"

# Expose the metrics port
EXPOSE 8001

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]