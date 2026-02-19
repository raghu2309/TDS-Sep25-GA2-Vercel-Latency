import json
import numpy as np
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "q-vercel-latency.json"


def handler(request):
    # ---- CORS ----
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }

    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": "",
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"error": "POST only"}),
        }

    body = request.json
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms")

    # ---- Load data ----
    with open(DATA_FILE) as f:
        records = json.load(f)

    response = {}

    for region in regions:
        region_records = [r for r in records if r["region"] == region]

        latencies = np.array([r["latency_ms"] for r in region_records])
        uptimes = np.array([r["uptime_pct"] for r in region_records])

        response[region] = {
            "avg_latency": float(latencies.mean()),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(uptimes.mean()),
            "breaches": int((latencies > threshold).sum()),
        }

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(response),
    }

