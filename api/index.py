
import json
import numpy as np
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "q-vercel-latency.json"


def handler(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }

    # CORS preflight
    if request.method == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"error": "POST only"}),
        }

    body = request.json
    regions = body["regions"]
    threshold = body["threshold_ms"]

    with open(DATA_FILE) as f:
        data = json.load(f)

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]

        lat = np.array([r["latency_ms"] for r in records])
        up = np.array([r["uptime_pct"] for r in records])

        result[region] = {
            "avg_latency": float(lat.mean()),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": float(up.mean()),
            "breaches": int((lat > threshold).sum()),
        }

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(result),
    }