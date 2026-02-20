"""
Deployment Tracker API
A simple REST API that tracks software deployments.
Built to demonstrate containerisation, Kubernetes deployment, and CI/CD pipelines.
"""

from flask import Flask, jsonify, request
import os
import datetime
import socket
import time

from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = Flask(__name__)

# In-memory store — in production this would be a database
# For this project, in-memory is fine because the focus is on
# the infrastructure and pipeline, not the data persistence
# comment test
deployments = []

# PROMETHEUS METRICS SETUP
# ============================================

# RED Method Metrics (Rate, Errors, Duration)

# RATE: Count of requests
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# DURATION: How long requests take
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]  # Response time buckets
)

# ERRORS: Count of failed requests
ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status']
)

# Business Metrics (specific to your app)
DEPLOYMENTS_CREATED = Counter(
    'deployments_created_total',
    'Total deployments created'
)

ACTIVE_DEPLOYMENTS = Gauge(
    'active_deployments',
    'Current number of active deployments'
)

# In-memory storage (you already have this from previous project)
deployments = []

# ============================================
# MIDDLEWARE: Track metrics for every request
# ============================================

@app.before_request
def before_request():
    """Start timing the request."""
    request.start_time = time.time()

@app.after_request
def after_request(response):
    """Record metrics after each request."""
    request_latency = time.time() - request.start_time
    endpoint = request.endpoint or 'unknown'
    
    # Record request count
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()
    
    # Record latency
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(request_latency)
    
    # Record errors (4xx and 5xx)
    if response.status_code >= 400:
        ERROR_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
    
    return response


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.

    WHY THIS EXISTS:
    Kubernetes uses this to determine if your pod is alive and ready
    to receive traffic. If this returns non-200, Kubernetes will:
    - Liveness probe failure: restart the pod
    - Readiness probe failure: stop sending traffic to this pod

    This is a CRITICAL concept in Kubernetes — every production app needs this.
    """
    return jsonify(
        {
            "status": "healthy",
            "hostname": socket.gethostname(),  # Shows which pod responded
            "version": os.getenv("APP_VERSION", "0.1.0"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
    )


@app.route("/api/deployments", methods=["GET"])
def get_deployments():
    """List all recorded deployments."""
    return jsonify({"count": len(deployments), "deployments": deployments})


@app.route("/api/deployments", methods=["POST"])
def create_deployment():
    """
    Record a new deployment.

    Example request body:
    {
        "service": "web-frontend",
        "version": "2.1.0",
        "environment": "production",
        "deployed_by": "github-actions"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    deployment = {
        "id": len(deployments) + 1,
        "service": data.get("service", "unknown"),
        "version": data.get("version", "0.0.0"),
        "environment": data.get("environment", "dev"),
        "deployed_by": data.get("deployed_by", "manual"),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "status": "success",
    }

    deployments.append(deployment)
    return jsonify(deployment), 201


@app.route("/api/info", methods=["GET"])
def info():
    """Application metadata — useful for debugging which version is running where."""
    return jsonify(
        {
            "app": "deployment-tracker",
            "version": os.getenv("APP_VERSION", "0.1.0"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "hostname": socket.gethostname(),
        }
    )


@app.route("/", methods=["GET"])
def root():
    """Root endpoint — simple landing page."""
    return jsonify(
        {
            "message": "Deployment Tracker API",
            "endpoints": {
                "health": "/health",
                "list_deployments": "GET /api/deployments",
                "create_deployment": "POST /api/deployments",
                "app_info": "/api/info",
            },
        }
    )

@app.route("/metrics")
def metrics():
    """
    Prometheus metrics endpoint.
    This is what Prometheus will scrape.
    """
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
