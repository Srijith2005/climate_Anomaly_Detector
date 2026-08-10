import os
from datetime import datetime, timezone
import requests
import pandas as pd

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

def fetch_weather_data(district_name, coords):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "wind_speed_10m",
        ],
        "timezone": "auto",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()["current"]
        return {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "city": district_name,
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "temp_c": data["temperature_2m"],
            "feels_like_c": data["apparent_temperature"],
            "humidity_pct": data["relative_humidity_2m"],
            "precipitation_mm": data["precipitation"],
            "wind_speed_kmh": data["wind_speed_10m"],
        }
    else:
        print(f"Failed to fetch data for {district_name}")
        return None 

def main():
    records = []
    for district_name, coords in DISTRICTS.items():
        data = fetch_weather_data(district_name, coords)
        if data:
            records.append(data)
            
    df = pd.DataFrame(records)

    print("\n--- Live Tamil Nadu Weather Data Extracted ---")
    print(df.to_string(index=False))

    file_path = "live_weather_log.csv"
    file_exists = os.path.exists(file_path)
    df.to_csv(file_path, mode="a", header=not file_exists, index=False)
    print(f"\nSuccessfully saved 38 district metrics to '{file_path}'.")

if __name__ == "__main__":
    main()