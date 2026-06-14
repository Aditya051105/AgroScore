import json
import urllib.parse
import urllib.request

DEMO_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aab825762a7e4ef6"


def get_mandi_price(crop, district):
    query = urllib.parse.urlencode({
        "api-key": DEMO_KEY,
        "format": "json",
        "commodity": crop,
        "district": district,
        "limit": 5,
    })
    url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?{query}"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            data = json.load(response)
        records = data.get("records", [])
        if records:
            sample = records[0]
            return {
                "crop": crop,
                "district": district,
                "price_per_quintal": float(sample.get("modal_price", sample.get("price", 2100))),
                "market": sample.get("market", "Local mandi"),
                "source": "Agmarknet",
            }
    except Exception:
        pass

    demo_prices = {
        "wheat": 2150,
        "soybean": 4200,
        "cotton": 6200,
        "onion": 1800,
        "tur": 7100,
        "maize": 1750,
    }
    return {
        "crop": crop,
        "district": district,
        "price_per_quintal": demo_prices.get(crop.lower(), 2500),
        "market": "Demo mandi",
        "source": "Demo mode",
        "note": "Agmarknet unavailable, showing sample mandi price.",
    }
