# main.py

import requests
from prometheus_client import (
    start_http_server,
    REGISTRY,
    Gauge,
    Counter,
    Summary,
    Histogram,
)
from prometheus_client.parser import text_string_to_metric_families
import time

# Configuration
import os

LLAMACPP_BASE_URL = os.getenv("LLAMACPP_BASE_URL", "http://localhost:8000")
MODELS_ENDPOINT = f"{LLAMACPP_BASE_URL}/models"
METRICS_ENDPOINT = f"{LLAMACPP_BASE_URL}/metrics"
SERVER_PORT = int(os.getenv("SERVER_PORT", "8001"))

# Store created metrics to avoid recreating them
created_metrics = {}


def fetch_model_ids():
    """Fetch model IDs from the /models endpoint, only for loaded models."""
    try:
        print(f"fetching models from {MODELS_ENDPOINT}")
        response = requests.get(MODELS_ENDPOINT)
        response.raise_for_status()

        data = response.json()

        # Extract model IDs from .data[].id structure, only for loaded models
        if isinstance(data, dict) and "data" in data:
            models_data = data["data"]
            if isinstance(models_data, list):
                loaded_models = []
                for model in models_data:
                    if "id" in model and "status" in model:
                        status = model["status"]
                        if isinstance(status, dict) and "value" in status:
                            if status["value"] == "loaded":
                                loaded_models.append(model["id"])
                                print(f"Found loaded model: {model['id']}")
                        elif status == "loaded":
                            # Handle case where status is directly the value
                            loaded_models.append(model["id"])
                            print(f"Found loaded model: {model['id']}")
                return loaded_models

        print(f"Unexpected models response format: {data}")
        return []

    except Exception as e:
        print(f"Error fetching model IDs: {e}")
        return []


def fetch_metrics(model_id):
    """Fetch metrics for a specific model ID."""
    try:
        print(f"fetching metrics for {model_id}")
        # Fetch metrics for the specific model using the correct parameter
        response = requests.get(f"{METRICS_ENDPOINT}?model={model_id}")
        response.raise_for_status()
        return response.text

    except Exception as e:
        print(f"Error fetching metrics for model {model_id}: {e}")
        return None


def update_metrics():
    """Fetch model IDs and update metrics for each model."""
    model_ids = fetch_model_ids()
    for model_id in model_ids:
        metrics_text = fetch_metrics(model_id)
        if metrics_text:
            # Parse metrics text using Prometheus parser
            metric_families = text_string_to_metric_families(metrics_text)

            # Process each metric family
            for metric_family in metric_families:
                metric_name = metric_family.name
                metric_type = metric_family.type

                # Get or create metric
                if metric_name not in created_metrics:
                    # Get all unique label names from samples
                    label_names = set()
                    for sample in metric_family.samples:
                        if sample.labels:
                            label_names.update(sample.labels.keys())
                    label_names.add("model")

                    if metric_type == "gauge":
                        created_metrics[metric_name] = Gauge(
                            metric_name,
                            metric_family.documentation,
                            list(label_names),
                        )
                    elif metric_type == "counter":
                        created_metrics[metric_name] = Counter(
                            metric_name,
                            metric_family.documentation,
                            list(label_names),
                        )
                    elif metric_type == "summary":
                        created_metrics[metric_name] = Summary(
                            metric_name,
                            metric_family.documentation,
                            list(label_names),
                        )
                    elif metric_type == "histogram":
                        created_metrics[metric_name] = Histogram(
                            metric_name,
                            metric_family.documentation,
                            list(label_names),
                        )
                    else:
                        continue

                metric = created_metrics[metric_name]

                # Add samples with model label
                for sample in metric_family.samples:
                    labels = sample.labels.copy() if sample.labels else {}
                    labels["model"] = model_id

                    # Handle different metric types appropriately
                    if metric_type == "gauge":
                        metric.labels(**labels).set(sample.value)
                    elif metric_type == "counter":
                         # To "copy" counter values exactly, we need to reset and then set
                         # Get the current counter object
                         counter = metric.labels(**labels)
                         # Reset by setting internal value to 0, then increment by observed value
                         counter._value.set(0)
                         counter.inc(sample.value)
                    elif metric_type == "summary":
                        metric.labels(**labels).observe(sample.value)
                    elif metric_type == "histogram":
                        metric.labels(**labels).observe(sample.value)


def main():
    """Main function to start the metrics server and update metrics periodically."""
    start_http_server(SERVER_PORT)
    print(f"Metrics server started on port {SERVER_PORT}")

    while True:
        update_metrics()
        time.sleep(15)


if __name__ == "__main__":
    main()
