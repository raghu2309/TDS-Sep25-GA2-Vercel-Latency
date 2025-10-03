from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load JSON data from repo root
DATA_FILE = Path("q-vercel-latency.json")
with open(DATA_FILE, "r") as f:
    DATA = json.load(f)

# POST endpoint for metrics
@app.post("/")
async def get_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    result = []

    for region in regions:
        region_data = [d for d in DATA if d.get("region") == region]

        if not region_data:
            continue

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime"] for d in region_data]
        breaches = sum(1 for l in latencies if l > threshold)

        result.append({
            "region": region,
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": sorted(latencies)[int(0.95 * len(latencies)) - 1],
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": breaches
        })

    return result

# 👇 THIS makes FastAPI work on Vercel
handler = Mangum(app
