import os
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import requests

DISTRICTS = {
    "Ariyalur": {"lat": 11.1401, "lon": 79.0786},
    "Chengalpattu": {"lat": 12.6825, "lon": 79.9822},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558},
    "Cuddalore": {"lat": 11.7480, "lon": 79.7714},
    "Dharmapuri": {"lat": 12.1211, "lon": 78.1582},
    "Dindigul": {"lat": 10.3673, "lon": 77.9803},
    "Erode": {"lat": 11.3410, "lon": 77.7172},
    "Kallakurichi": {"lat": 11.7384, "lon": 78.9639},
    "Kanchipuram": {"lat": 12.8342, "lon": 79.7036},
    "Kanniyakumari": {"lat": 8.0883, "lon": 77.5385},
    "Karur": {"lat": 10.9601, "lon": 78.0766},
    "Krishnagiri": {"lat": 12.5266, "lon": 78.2146},
    "Madurai": {"lat": 9.9252, "lon": 78.1198},
    "Mayiladuthurai": {"lat": 11.1018, "lon": 79.6521},
    "Nagapattinam": {"lat": 10.7656, "lon": 79.8424},
    "Namakkal": {"lat": 11.2189, "lon": 78.1674},
    "Nilgiris": {"lat": 11.4916, "lon": 76.7337},
    "Perambalur": {"lat": 11.2342, "lon": 78.8821},
    "Pudukkottai": {"lat": 10.3833, "lon": 78.8000},
    "Ramanathapuram": {"lat": 9.3639, "lon": 78.8395},
    "Ranipet": {"lat": 12.9224, "lon": 79.3331},
    "Salem": {"lat": 11.6643, "lon": 78.1460},
    "Sivaganga": {"lat": 9.8433, "lon": 78.4809},
    "Tenkasi": {"lat": 8.9593, "lon": 77.3153},
    "Thanjavur": {"lat": 10.7870, "lon": 79.1378},
    "Theni": {"lat": 10.0104, "lon": 77.4768},
    "Thoothukudi": {"lat": 8.7642, "lon": 78.1348},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047},
    "Tirunelveli": {"lat": 8.7139, "lon": 77.7567},
    "Tirupathur": {"lat": 12.4926, "lon": 78.5683},
    "Tiruppur": {"lat": 11.1085, "lon": 77.3411},
    "Tiruvallur": {"lat": 13.1432, "lon": 79.9098},
    "Tiruvannamalai": {"lat": 12.2253, "lon": 79.0747},
    "Tiruvarur": {"lat": 10.7711, "lon": 79.6364},
    "Vellore": {"lat": 12.9165, "lon": 79.1325},
    "Viluppuram": {"lat": 11.9401, "lon": 79.4861},
    "Virudhunagar": {"lat": 9.5680, "lon": 77.9624}
}

def fetch_live_batch():
    names = list(DISTRICTS.keys())
    lats = [str(DISTRICTS[k]["lat"]) for k in names]
    lons = [str(DISTRICTS[k]["lon"]) for k in names]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": ",".join(lats),
        "longitude": ",".join(lons),
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m",
        "timezone": "auto",
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    results = response.json()

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    records = []
    
    for name, item in zip(names, results):
        cur = item.get("current", {})
        records.append({
            "timestamp": now_utc,
            "city": name,
            "latitude": DISTRICTS[name]["lat"],
            "longitude": DISTRICTS[name]["lon"],
            "temp_c": cur.get("temperature_2m"),
            "feels_like_c": cur.get("apparent_temperature"),
            "humidity_pct": cur.get("relative_humidity_2m"),
            "precipitation_mm": cur.get("precipitation"),
            "wind_speed_kmh": cur.get("wind_speed_10m"),
        })
    return pd.DataFrame(records)

def detect_anomalies(df):
    # Historical district baseline references (mean and standard deviation)
    mean_temp = df["temp_c"].mean()
    std_temp = df["temp_c"].std() if df["temp_c"].std() != 0 else 1.0

    # Calculate Z-Score
    df["temp_zscore"] = ((df["temp_c"] - mean_temp) / std_temp).round(2)

    # Anomaly condition flags
    df["is_heat_anomaly"] = df["temp_zscore"] >= 1.5
    df["is_cold_anomaly"] = df["temp_zscore"] <= -1.5
    df["is_rain_anomaly"] = df["precipitation_mm"] > 20.0
    
    # Combined alert status for Power BI display
    conditions = [
        df["is_heat_anomaly"],
        df["is_cold_anomaly"],
        df["is_rain_anomaly"]
    ]
    choices = ["Heat Alert", "Cold Wave", "Heavy Rain"]
    df["anomaly_status"] = np.select(conditions, choices, default="Normal")
    
    return df

def main():
    print("Running anomaly detection pipeline...", flush=True)
    df_live = fetch_live_batch()
    
    # Also log raw live reading
    raw_path = "live_weather_log.csv"
    df_live.to_csv(raw_path, mode="a", header=not os.path.exists(raw_path), index=False)
    
    # Compute anomalies and save primary dataset for Power BI
    df_anomalies = detect_anomalies(df_live)
    out_path = "weather_anomalies.csv"
    df_anomalies.to_csv(out_path, index=False)
    
    print(f"Generated {out_path} with {len(df_anomalies)} records.", flush=True)

if __name__ == "__main__":
    main()