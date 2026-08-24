import os
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import requests

DISTRICTS = {
    "Ariyalur": {"lat": 11.1401, "lon": 79.0786, "zone": "South / Central TN"},
    "Chengalpattu": {"lat": 12.6825, "lon": 79.9822, "zone": "North TN"},
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "zone": "North TN"},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558, "zone": "Hilly / High Altitude"},
    "Cuddalore": {"lat": 11.7480, "lon": 79.7714, "zone": "North TN"},
    "Dharmapuri": {"lat": 12.1211, "lon": 78.1582, "zone": "North TN"},
    "Dindigul": {"lat": 10.3673, "lon": 77.9803, "zone": "South / Central TN"},
    "Erode": {"lat": 11.3410, "lon": 77.7172, "zone": "South / Central TN"},
    "Kallakurichi": {"lat": 11.7384, "lon": 78.9639, "zone": "North TN"},
    "Kanchipuram": {"lat": 12.8342, "lon": 79.7036, "zone": "North TN"},
    "Kanniyakumari": {"lat": 8.0883, "lon": 77.5385, "zone": "South / Central TN"},
    "Karur": {"lat": 10.9601, "lon": 78.0766, "zone": "South / Central TN"},
    "Krishnagiri": {"lat": 12.5266, "lon": 78.2146, "zone": "North TN"},
    "Madurai": {"lat": 9.9252, "lon": 78.1198, "zone": "South / Central TN"},
    "Mayiladuthurai": {"lat": 11.1018, "lon": 79.6521, "zone": "South / Central TN"},
    "Nagapattinam": {"lat": 10.7656, "lon": 79.8424, "zone": "South / Central TN"},
    "Namakkal": {"lat": 11.2189, "lon": 78.1674, "zone": "South / Central TN"},
    "Nilgiris": {"lat": 11.4916, "lon": 76.7337, "zone": "Hilly / High Altitude"},
    "Perambalur": {"lat": 11.2342, "lon": 78.8821, "zone": "South / Central TN"},
    "Pudukkottai": {"lat": 10.3833, "lon": 78.8000, "zone": "South / Central TN"},
    "Ramanathapuram": {"lat": 9.3639, "lon": 78.8395, "zone": "South / Central TN"},
    "Ranipet": {"lat": 12.9224, "lon": 79.3331, "zone": "North TN"},
    "Salem": {"lat": 11.6643, "lon": 78.1460, "zone": "South / Central TN"},
    "Sivaganga": {"lat": 9.8433, "lon": 78.4809, "zone": "South / Central TN"},
    "Tenkasi": {"lat": 8.9593, "lon": 77.3153, "zone": "South / Central TN"},
    "Thanjavur": {"lat": 10.7870, "lon": 79.1378, "zone": "South / Central TN"},
    "Theni": {"lat": 10.0104, "lon": 77.4768, "zone": "South / Central TN"},
    "Thoothukudi": {"lat": 8.7642, "lon": 78.1348, "zone": "South / Central TN"},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047, "zone": "South / Central TN"},
    "Tirunelveli": {"lat": 8.7139, "lon": 77.7567, "zone": "South / Central TN"},
    "Tirupathur": {"lat": 12.4926, "lon": 78.5683, "zone": "North TN"},
    "Tiruppur": {"lat": 11.1085, "lon": 77.3411, "zone": "South / Central TN"},
    "Tiruvallur": {"lat": 13.1432, "lon": 79.9098, "zone": "North TN"},
    "Tiruvannamalai": {"lat": 12.2253, "lon": 79.0747, "zone": "North TN"},
    "Tiruvarur": {"lat": 10.7711, "lon": 79.6364, "zone": "South / Central TN"},
    "Vellore": {"lat": 12.9165, "lon": 79.1325, "zone": "North TN"},
    "Viluppuram": {"lat": 11.9401, "lon": 79.4861, "zone": "North TN"},
    "Virudhunagar": {"lat": 9.5680, "lon": 77.9624, "zone": "South / Central TN"}
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

    records = []
    for name, item in zip(names, results):
        cur = item.get("current", {})
        records.append({
            "city": name,
            "latitude": DISTRICTS[name]["lat"],
            "longitude": DISTRICTS[name]["lon"],
            "Terrain_Zone": DISTRICTS[name]["zone"],
            "current_temp_c": cur.get("temperature_2m"),
            "feels_like_c": cur.get("apparent_temperature"),
            "humidity_pct": cur.get("relative_humidity_2m"),
            "precipitation_mm": cur.get("precipitation"),
            "wind_speed_kmh": cur.get("wind_speed_10m"),
        })
    return pd.DataFrame(records)

def detect_anomalies(df):
    # 10-Year historical baseline mock mean (~28.5 C standard reference for TN)
    df["baseline_mean_c"] = 28.50
    baseline_std = 2.50

    # Calculate Z-Score against baseline
    df["z_score"] = ((df["current_temp_c"] - df["baseline_mean_c"]) / baseline_std).round(2)
    
    # Anomaly flags matching Power BI columns
    df["is_anomaly"] = df["z_score"].abs() >= 1.5
    
    conditions = [
        df["z_score"] >= 2.5,
        (df["z_score"] >= 1.5) & (df["z_score"] < 2.5),
        df["z_score"] <= -1.5,
    ]
    choices = ["Extreme Heat", "Moderate Heat", "Cold Wave"]
    df["Anomaly_Severity"] = np.select(conditions, choices, default="Normal")
    
    return df

def main():
    print("Fetching batch weather data and calculating anomalies...", flush=True)
    df = fetch_live_batch()
    df = detect_anomalies(df)
    
    out_path = "weather_anomalies.csv"
    df.to_csv(out_path, index=False)
    print(f"Generated {out_path} with {len(df)} records matching Power BI schema.", flush=True)

if __name__ == "__main__":
    main()