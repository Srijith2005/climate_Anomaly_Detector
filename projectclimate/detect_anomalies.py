import os
from datetime import datetime, timedelta
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

def get_historical_baseline(lat, lon):
    end_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=3650)).strftime("%Y-%m-%d")
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_mean",
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        daily_temps = response.json()["daily"]["temperature_2m_mean"]
        s = pd.Series(daily_temps).dropna()
        return round(s.mean(), 2), round(s.std(), 2)
    return None, None

def main():
    if not os.path.exists("live_weather_log.csv"):
        print("Error: live_weather_log.csv not found!")
        return

    live_df = pd.read_csv("live_weather_log.csv")
    
    latest_df = live_df.sort_values("timestamp").groupby("city").last().reset_index()
    
    results = []
    print("\n--- Computing 10-Year Baselines & Z-Scores for Tamil Nadu Districts ---")
    
    for _, row in latest_df.iterrows():
        city = row["city"]
        current_temp = row["temp_c"]
        lat = row["latitude"]
        lon = row["longitude"]
        
        print(f"Processing {city}...")
        mean_temp, std_temp = get_historical_baseline(lat, lon)
        
        if mean_temp is not None and std_temp is not None and std_temp > 0:
            z_score = round((current_temp - mean_temp) / std_temp, 2)
            is_anomaly = abs(z_score) >= 2.0
        else:
            z_score = 0.0
            is_anomaly = False
            
        results.append({
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "current_temp_c": current_temp,
            "baseline_mean_c": mean_temp,
            "baseline_std": std_temp,
            "z_score": z_score,
            "is_anomaly": is_anomaly
        })
        
    out_df = pd.DataFrame(results)
    out_df.to_csv("weather_anomalies.csv", index=False)
    print("\nSuccessfully updated 'weather_anomalies.csv' with all 38 districts!")

if __name__ == "__main__":
    main()