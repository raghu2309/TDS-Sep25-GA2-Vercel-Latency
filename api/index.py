from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from pathlib import Path

app = FastAPI()

# Enable CORS for dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load data at startup
import json
from pathlib import Path

# The JSON file is in the repo root, so just reference it directly
DATA_FILE = Path("q-vercel-latency.json")
with open(DATA_FILE, "r") as f:
    DATA = json.load(f)

@app.post("/")
async def get_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    results = {}
    for region in regions:
        region_data = [d for d in DATA if d.get("region") == region]
        if not region_data:
            continue

        latencies = [d["latency"] for d in region_data]
        uptimes = [d["uptime"] for d in region_data]

        metrics = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold),
        }
        results[region] = metrics

    return results
