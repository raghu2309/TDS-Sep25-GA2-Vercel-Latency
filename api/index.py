
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
from typing import List, Dict

app = FastAPI()

# Enable CORS for all origins (any website), but only for POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # any origin
    allow_methods=["POST"],   # only POST
    allow_headers=["*"],
)

# Define what the request body should look like
class TelemetryRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

# Load telemetry file once at startup
with open("q-vercel-latency.json", "r") as f:
    telemetry_data = json.load(f)

@app.post("/analytics")
def analytics(req: TelemetryRequest) -> Dict[str, Dict[str, float]]:
    """
    Example input:
    {
      "regions": ["apac", "emea"],
      "threshold_ms": 183
    }
    """

    result = {}

    for region in req.regions:
        # Filter records that belong to this region
        region_records = [r for r in telemetry_data if r.get("region") == region]

        if not region_records:
            # If no data for this region, return zeros or skip
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0,
            }
            continue

        # Extract latency and uptime values
        latencies = [r["latency_ms"] for r in region_records]
        uptimes = [r["uptime"] for r in region_records]

        # Compute mean (average) latency
        avg_latency = float(np.mean(latencies))

        # Compute 95th percentile latency
        p95_latency = float(np.percentile(latencies, 95))

        # Compute mean (average) uptime
        avg_uptime = float(np.mean(uptimes))

        # Count breaches: how many latencies > threshold_ms
        breaches = sum(1 for v in latencies if v > req.threshold_ms)

        # Store results for this region
        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }

    return result
