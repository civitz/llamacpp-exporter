# llamacpp-exporter

A Prometheus exporter for llama.cpp models that consolidates metrics from multiple models into a single endpoint.

## Features

- Fetches metrics only from loaded models (status.value == "loaded")
- Adds model labels to all metrics
- Configurable base URL and server port
- Lightweight Docker image based on Python Alpine (~50MB)
- Simple deployment - no compilation needed

## Prerequisites

- Docker (for containerized deployment)
- Python 3.8+ (for local development)

## Quick Start

### Using Docker

```bash
# Build the Docker image
make build

# Run the container
docker run -it --rm \
  -p 8001:8001 \
  -e LLAMACPP_BASE_URL="http://host.docker.internal:8000" \
  -e SERVER_PORT="8001" \
  llamacpp-exporter:latest
```

**Note**: The Docker image uses `python:3-alpine` as base and runs the Python script directly with all dependencies installed.

### Local Development

```bash
# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install requests prometheus-client

# Run the exporter directly
source .venv/bin/activate
python main.py
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLAMACPP_BASE_URL` | `http://localhost:8000` | Base URL for the llama.cpp server |
| `SERVER_PORT` | `8001` | Port for the metrics server |

### API Endpoints

- **Models**: `GET /models` - Returns model list with status
- **Metrics**: `GET /metrics?model=<model_id>` - Returns metrics for a specific model

## Metrics

The exporter exposes all metrics from the llama.cpp server with an additional `model` label indicating the model ID. Metrics are available at `http://localhost:8001/metrics`.

## Makefile Targets

| Target | Description |
|--------|-------------|
| `all` | Build the Docker image (default) |
| `build` | Build the Docker image |
| `clean` | Clean build artifacts |
| `run` | Run the Docker container |
| `package` | Package the Docker image as a tar.gz file |

## Docker Usage

### Build
```bash
make build
```

### Run
```bash
make run
```

### Package for Distribution
```bash
make package
```

## Development

The exporter only processes models that are in the "loaded" state (`status.value == "loaded"`). This ensures efficient resource usage by not attempting to fetch metrics from models that aren't ready.

## License

MIT