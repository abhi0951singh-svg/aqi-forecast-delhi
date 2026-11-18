import json
from pathlib import Path
import joblib
import pandas as pd
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed" / "pm25_hourly_clean.csv"
MODELS = ROOT / "backend" / "models"
MODELS.mkdir(parents=True, exist_ok=True)

HORIZON = 24
LAGS = [1, 2, 3, 6, 12, 24, 48]

def make_features(s):
    X = pd.DataFrame({"now": s})
    for k in LAGS:
        X[f"lag_{k}"] = s.shift(k)
    X["change_1h"] = s - s.shift(1)
    X["change_24h"] = s - s.shift(24)
    X["roll_mean_24"] = s.rolling(24).mean()
    X["roll_std_24"] = s.rolling(24).std()
    X["hour"] = X.index.hour
    return X

df = pd.read_csv(DATA)
df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_convert("Asia/Kolkata")

forecasts = []
for station, g in df.groupby("station"):
    s = g.sort_values("time").set_index("time")["pm25"]
    X = make_features(s)
    X["target_change"] = s.shift(-HORIZON) - s
    features = [c for c in X.columns if c != "target_change"]

    model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=3,
                         subsample=0.8, random_state=42)
    train = X.dropna()
    model.fit(train[features], train["target_change"])

    name = station.split(",")[0].replace(" ", "_")
    joblib.dump({"model": model, "features": features}, MODELS / f"{name}.joblib")

    last = X[features].dropna().iloc[[-1]]
    now = float(last["now"].iloc[0])
    pred = max(0.0, now + float(model.predict(last)[0]))
    forecasts.append({
        "station": station,
        "as_of": last.index[0].isoformat(),
        "current_pm25": round(now, 1),
        "forecast_pm25_24h": round(pred, 1),
    })
    print("Saved model for", station)

out = ROOT / "data" / "processed" / "latest_forecast.json"
out.write_text(json.dumps(forecasts, indent=2))
print("Wrote", out)