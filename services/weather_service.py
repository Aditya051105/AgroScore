import json
import urllib.request

DISTRICT_LAT_LNG = {
    "Amravati": (20.9334, 77.7523),
    "Nagpur": (21.1458, 79.0882),
    "Yavatmal": (20.3888, 78.1204),
    "Akola": (20.7002, 77.0082),
    "Wardha": (20.7453, 78.6022),
    "Bhopal": (23.2599, 77.4126),
    "Indore": (22.7196, 75.8577),
    "Jabalpur": (23.1815, 79.9861),
    "Ujjain": (23.1793, 75.7849),
    "Gwalior": (26.2183, 78.1828),
}


def get_weather_for_district(district):
    lat, lng = DISTRICT_LAT_LNG.get(district, (23.2599, 77.4126))
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&daily=precipitation_sum,temperature_2m_max&timezone=Asia/Kolkata"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            data = json.load(response)
        daily = data.get("daily", {})
        return {
            "district": district,
            "temperature_max": daily.get("temperature_2m_max", [30])[0],
            "rainfall": daily.get("precipitation_sum", [0])[0],
            "source": "Open-Meteo",
        }
    except Exception:
        return {
            "district": district,
            "temperature_max": 31,
            "rainfall": 2.5,
            "source": "Demo mode",
            "note": "External weather API unavailable, showing sample data.",
        }
