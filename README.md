# Delhi-NCR AQI Monitoring and Forecasting Dashboard

A web dashboard that shows current air quality and forecasts PM2.5 24 hours
ahead for stations in Delhi-NCR.

**Live dashboard:** https://abhi0951singh-svg.github.io/aqi-forecast-delhi/
**Live API:** https://aqi-forecast-delhi.onrender.com/stations

## Problem
Public air quality tools mostly show current readings only, with little
short-term forecasting. This project collects, cleans and forecasts PM2.5
for four Delhi-NCR stations and presents it on a map-based dashboard.

## Data
- Source: [OpenAQ](https://openaq.org) API, hourly PM2.5
- Stations: Anand Vihar, New Delhi, Punjabi Bagh, R K Puram
- Period: roughly Oct 2025 to Oct 2026 (about one year, hourly)

## Method
- Cleaning: invalid values removed, converted to IST, gaps up to 3 hours filled
- Baseline: persistence model ("PM2.5 in 24h = PM2.5 now")
- Models: Random Forest and XGBoost, trained on lag, rolling and trend
  features, with a time-based 80/20 train/test split
- Target: predicted change from "now", added back to the current value

## Results (MAE, µg/m³, lower is better)

| Station       | Baseline | Random Forest | XGBoost |
|---------------|----------|----------------|---------|
| Anand Vihar   | 30.2     | 25.0           | 24.2    |
| New Delhi     | 14.6     | 14.5           | 14.2    |
| Punjabi Bagh  | 23.5     | 21.1           | 21.2    |
| R K Puram     | 20.5     | 19.1           | 19.2    |

Models beat the baseline at all four stations, modestly (3-20%). Results
are on the cleaner months (roughly Jun-Oct); winter evaluation is future work.

## Tech stack
- **Data & ML:** Python, pandas, scikit-learn, XGBoost
- **Backend:** FastAPI, deployed on Render
- **Frontend:** HTML, JavaScript, Leaflet, deployed on GitHub Pages

## Project structure


## Limitations and future work
- Forecasts PM2.5 only, not the full AQI
- No weather features yet (planned: temperature, humidity, wind)
- Not yet tested on winter data, when pollution is highest
- One station (New Delhi) stopped reporting around August 2026

## Author
Abhishek Kumar Singh, DIT University, Dehradun — Capstone Project (UCF 439)