import os
import numpy as np
import pandas as pd
import requests

# 38 Tamil Nadu Districts with Terrain Classification & Seasonal Mean/Std Baselines
DISTRICTS = {
    "Ariyalur": {"lat": 11.1401, "lon": 79.0786, "zone": "South / Central TN", "base_mean": 28.5, "base_std": 2.2},
    "Chengalpattu": {"lat": 12.6825, "lon": 79.9822, "zone": "North TN", "base_mean": 28.0, "base_std": 2.0},
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "zone": "North TN", "base_mean": 28.2, "base_std": 2.0},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558, "zone": "Hilly / High Altitude", "base_mean": 24.5, "base_std": 2.0},
    "Cuddalore": {"lat": 11.7480, "lon": 79.7714, "zone": "North TN", "base_mean": 28.0, "base_std": 2.1},
    "Dharmapuri": {"lat": 12.1211, "lon": 78.1582, "zone": "North TN", "base_mean": 26.5, "base_std": 2.2},
    "Dindigul": {"lat": 10.3673, "lon": 77.9803, "zone": "South / Central TN", "base_mean": 27.5, "base_std": 2.2},
    "Erode": {"lat": 11.3410, "lon": 77.7172, "zone": "South / Central TN", "base_mean": 27.5, "base_std": 2.2},
    "Kallakurichi": {"lat": 11.7384, "lon": 78.9639, "zone": "North TN", "base_mean": 28.0, "base_std": 2.2},
    "Kanchipuram": {"lat": 12.8342, "lon": 79.7036, "zone": "North TN", "base_mean": 28.0, "base_std": 2.1},
    "Kanniyakumari": {"lat": 8.0883, "lon": 77.5385, "zone": "South / Central TN", "base_mean": 27.0, "base_std": 1.8},
    "Karur": {"lat": 10.9601, "lon": 78.0766, "zone": "South / Central TN", "base_mean": 28.5, "base_std": 2.3},
    "Krishnagiri": {"lat": 12.5266, "lon": 78.2146, "zone": "North TN", "base_mean": 25.8, "base_std": 2.2},
    "Madurai": {"lat": 9.9252, "lon": 78.1198, "zone": "South / Central TN", "base_mean": 28.8, "base_std": 2.2},
    "Mayiladuthurai": {"lat": 11.1018, "lon": 79.6521, "zone": "South / Central TN", "base_mean": 28.0, "base_std": 2.0},
    "Nagapattinam": {"lat": 10.7656, "lon": 79.8424, "zone": "South / Central TN", "base_mean": 28.0, "base_std": 2.0},
    "Namakkal": {"lat": 11.2189, "lon": 78.1674, "zone": "South / Central TN", "base_mean": 28.0, "base_std": 2.2},
    "Nilgiris": {"lat": 11.4916, "lon": 76.7337, "zone": "Hilly / High Altitude", "base_mean": 15.5, "base_std": 2.0},
    "Perambalur": {"lat": 11.2342, "lon": 78.8821, "zone": "South / Central TN", "base_mean": 28.2, "base_std": 2.2},
    "Pudukkottai": {"lat": 10.3833, "lon": 78.8000, "zone": "South / Central TN", "base_mean": 28.5, "base_std": 2.1},
    "Ramanathapuram": {"lat": 9.3639, "lon": 78.8395, "zone": "South / Central TN", "base_mean": 28.5, "base_std": 2.0},
    "Ranipet": {"lat": 12.9224, "lon": 79.3331, "zone": "North TN", "base_mean": 28.0, "base_std": 2.2},
    "Salem": {"lat": 11.6643, "lon": 78.1460, "zone": "South / Central TN", "base_mean": 27.5, "base_std": 2.2},
    "Sivaganga": {"lat": 9.8433, "lon": 78.4809, "zone": "South / Central TN", "base_mean": 28.5, "base_std": 2.2},
    "Tenkasi": {"lat": 8.9593, "lon": 77.3153, "zone": "South / Central TN", "base_mean": 27.0, "base_std": 2.0},
    "Thanjavur": {"lat": 10.7870, "lon": 79.1378, "zone": "South / Central TN", "base_mean": 28.5, "base_std": 2.1},
    "Theni": {"lat": 10.0104, "lon": 77.4768, "zone": "South / Central TN", "base_mean": 26.5, "base_std": 2.2},
    "Thoothukudi": {"lat": 8.7642, "lon": 78.1348, "zone": "South / Central TN", "base_mean": 28.2, "base_std": 1.9},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047, "zone": "South / Central TN", "base_mean": 28.8, "base_std": 2.3},
    "Tirunelveli": {"lat": 8.7139, "lon": 77.7567, "zone": "South / Central TN", "base_mean": 28.5, "base_std": 2.1},
    "Tirupathur": {"lat": 12.4926, "lon": 78.5683, "zone": "North TN", "base_mean": 27.5, "base_std": 2.2},
    "Tiruppur": {"lat": 11.1085, "lon": 77.3411, "zone": "South / Central TN", "base_mean": 27.0, "base_std": 2.1},
    "Tiruvallur": {"lat": 13.1432, "lon": 79.9098, "zone": "North TN", "base_mean": 28.0, "base_std": 2.1},
    "Tiruvannamalai": {"lat": 12.2253, "lon": 79.0747, "zone": "North TN", "base_mean": 28.0, "base_std": 2.2},
    "Tiruvarur": {"lat": 10.7711, "lon": 79.6364, "zone": "South / Central TN", "base_mean": 28.0, "base_std": 2.0},
    "Vellore": {"lat": 12.9165, "lon": 79.1325, "zone": "North TN", "base_mean": 28.2, "base_std": 2.3},
    "Viluppuram": {"lat": 11.9401, "lon": 79.4861, "zone": "North TN", "base_mean": 28.0, "base_std": 2.2},
    "Virudhunagar": {"lat": 9.5680, "lon": 77.9624, "zone": "South / Central TN", "base_mean": 28.8, "base_std": 2.2}
}

def fetch_live_data():
    names = list(DISTRICTS.keys())
    lats = [str(DISTRICTS[k]["lat"]) for k in names]
    lons = [str(DISTRICTS[k]["lon"]) for k in names]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": ",".join(lats),
        "longitude": ",".join(lons),
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m",
        "timezone": "Asia/Kolkata",
    }

    response = requests.get(url, params=params, timeout=25)
    response.raise_for_status()
    results = response.json()

    # Open-Meteo returns a list for bulk queries, or a single dict if one coordinate
    if isinstance(results, dict):
        results = [results]

    records = []
    for name, item in zip(names, results):
        cur = item.get("current", {})
        temp = float(cur.get("temperature_2m", DISTRICTS[name]["base_mean"]))
        baseline = float(DISTRICTS[name]["base_mean"])
        std = float(DISTRICTS[name]["base_std"])
        
        # Calculate statistical anomaly (z-score)
        z = round((temp - baseline) / std, 2)
        
        # Anomaly categorization
        if z >= 2.5:
            severity = "Extreme Heat"
        elif z >= 1.5:
            severity = "Moderate Heat"
        elif z <= -1.5:
            severity = "Cold Wave"
        else:
            severity = "Normal"

        records.append({
            "city": name,
            "latitude": DISTRICTS[name]["lat"],
            "longitude": DISTRICTS[name]["lon"],
            "Terrain_Zone": DISTRICTS[name]["zone"],
            "current_temp_c": round(temp, 2),
            "baseline_mean_c": baseline,
            "baseline_std": std,
            "z_score": z,
            "is_anomaly": abs(z) >= 1.5,
            "Anomaly_Severity": severity,
            "feels_like_c": cur.get("apparent_temperature"),
            "humidity_pct": cur.get("relative_humidity_2m"),
            "precipitation_mm": cur.get("precipitation"),
            "wind_speed_kmh": cur.get("wind_speed_10m")
        })
    
    return pd.DataFrame(records)

if __name__ == "__main__":
    df = fetch_live_data()
    df.to_csv("weather_anomalies.csv", index=False)
    print(f"Successfully generated weather_anomalies.csv with {len(df)} districts.")
