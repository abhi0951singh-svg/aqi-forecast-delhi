import json
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "backend" / "models"
DATA = ROOT / "data" / "processed"

DROP_STATIONS = {"New Delhi"}   # stopped reporting; excluded from the live dashboard

app = FastAPI(title="Delhi AQI Forecast API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_forecasts():
    data = json.loads((DATA / "latest_forecast.json").read_text())
    return [f for f in data if f["station"] not in DROP_STATIONS]

def load_station_locations():
    df = pd.read_csv(DATA / "stations.csv")
    return {row["name"]: (row["lat"], row["lon"]) for _, row in df.iterrows()}

def pm25_category(pm25: float) -> str:
    if pm25 <= 30:   return "Good"
    if pm25 <= 60:   return "Satisfactory"
    if pm25 <= 90:   return "Moderate"
    if pm25 <= 120:  return "Poor"
    if pm25 <= 250:  return "Very Poor"
    return "Severe"

@app.get("/")
def home():
    return {"message": "Delhi AQI Forecast API is running. See /docs for the endpoints."}

@app.get("/stations")
def get_stations():
    forecasts = load_forecasts()
    locations = load_station_locations()
    out = []
    for f in forecasts:
        lat, lon = locations.get(f["station"], (None, None))
        out.append({
            "station": f["station"],
            "lat": lat,
            "lon": lon,
            "current_pm25": f["current_pm25"],
            "forecast_pm25_24h": f["forecast_pm25_24h"],
            "current_category": pm25_category(f["current_pm25"]),
            "forecast_category": pm25_category(f["forecast_pm25_24h"]),
            "as_of": f["as_of"],
        })
    return out

@app.get("/stations/{station_name}/forecast")
def get_forecast(station_name: str):
    forecasts = load_forecasts()
    for f in forecasts:
        if station_name.lower() in f["station"].lower():
            return f
    raise HTTPException(status_code=404, detail="Station not found")