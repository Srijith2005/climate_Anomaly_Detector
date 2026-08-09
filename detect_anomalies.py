from datetime import datetime, timedelta
import os
import pandas as pd
import requests

CITIES = [
    {"city": "New York", "lat": 40.7128, "lon": -74.0060},
    {"city": "London", "lat": 51.5074, "lon": -0.1278},
    {"city": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"city": "Coimbatore", "lat": 11.0168, "lon": 76.9558},
    {"city": "Sydney", "lat": -33.8688, "lon": 151.2093},
]


def fetch_historical_baseline(lat, lon):
  url = "https://archive-api.open-meteo.com/v1/archive"

  today = datetime.utcnow().date()
  end_date = today - timedelta(days=2)
  start_date = end_date - timedelta(days=365 * 10)  # 10 years of history

  params = {
      "latitude": lat,
      "longitude": lon,
      "start_date": start_date.strftime("%Y-%m-%d"),
      "end_date": end_date.strftime("%Y-%m-%d"),
      "daily": "temperature_2m_mean",
      "timezone": "auto",
  }

  response = requests.get(url, params=params)
  if response.status_code == 200:
    data = response.json()["daily"]["temperature_2m_mean"]
    temps = pd.Series(data).dropna()
    return temps.mean(), temps.std()
  else:
    print(f"Error fetching archive data for lat: {lat}, lon: {lon}")
    return None, None


def main():
  live_file = "live_weather_log.csv"

  if not os.path.exists(live_file):
    print(
        f"Error: '{live_file}' not found. Please run fetch_live_data.py first!"
    )
    return

  df_live = pd.read_csv(live_file)

  # Get the latest weather reading for each city
  df_latest = df_live.groupby("city").last().reset_index()

  results = []
  print("\nFetching 10-year climate archives & calculating Z-scores...\n")

  for _, row in df_latest.iterrows():
    city = row["city"]
    lat, lon = row["latitude"], row["longitude"]
    current_temp = row["temp_c"]

    mean_temp, std_temp = fetch_historical_baseline(lat, lon)

    if mean_temp is not None and std_temp is not None:
      # Z-score formula: (Current - Mean) / StdDev
      z_score = (current_temp - mean_temp) / std_temp

      # Anomaly flag: if temperature is > 2 standard deviations away from normal
      is_anomaly = abs(z_score) > 2.0
      results.append({
          "city": city,
          "latitude": lat,
          "longitude": lon,
          "current_temp_c": current_temp,
          "baseline_mean_c": round(mean_temp, 2),
          "baseline_std": round(std_temp, 2),
          "z_score": round(z_score, 2),
          "is_anomaly": is_anomaly,
      })

  df_results = pd.DataFrame(results)
  print("--- Anomaly Detection Analysis ---")
  print(df_results.to_string(index=False))

  # Save to CSV for Power BI
  output_file = "weather_anomalies.csv"
  df_results.to_csv(output_file, index=False)
  print(f"\nSuccessfully created dataset '{output_file}'.")


if __name__ == "__main__":
  main()