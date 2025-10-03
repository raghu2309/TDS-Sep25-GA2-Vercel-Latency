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

@app.get("/message/")
def get_message(text: str):
    return {"response": f"You said: {text}"}
