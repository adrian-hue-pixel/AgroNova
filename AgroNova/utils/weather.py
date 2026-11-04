"""Live local weather for AgroNova, using the free Open-Meteo service (no API key needed).

- geocode()        place name -> latitude / longitude
- fetch_forecast() current weather + 7-day daily forecast, normalised to plain Python data
- farm_alerts()    simple, transparent rules that turn the forecast into watering / spraying / harvest hints
- forecast_for_prompt() the forecast written as text for Gemini (so it never has to invent weather)

Everything except the two network functions is pure Python and unit-tested with a sample response.
Open-Meteo data is licensed CC BY 4.0 - the app shows the attribution.
"""
import certifi
import datetime
import ssl
import json
import urllib.error
import urllib.parse
import urllib.request
import time

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ATTRIBUTION = "Weather data by Open-Meteo.com (CC BY 4.0)"

CURRENT_VARS = "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
DAILY_VARS = ("weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,"
              "precipitation_probability_max,wind_speed_10m_max")

# WMO weather interpretation codes -> (plain words, icon key)
_CODES = {
    0: ("Clear sky", "sun"), 1: ("Mostly clear", "sun"), 2: ("Partly cloudy", "partly"), 3: ("Overcast", "cloud"),
    45: ("Fog", "fog"), 48: ("Fog", "fog"),
    51: ("Light drizzle", "rain"), 53: ("Drizzle", "rain"), 55: ("Heavy drizzle", "rain"),
    56: ("Freezing drizzle", "rain"), 57: ("Freezing drizzle", "rain"),
    61: ("Light rain", "rain"), 63: ("Rain", "rain"), 65: ("Heavy rain", "rain"),
    66: ("Freezing rain", "rain"), 67: ("Freezing rain", "rain"),
    71: ("Light snow", "snow"), 73: ("Snow", "snow"), 75: ("Heavy snow", "snow"), 77: ("Snow grains", "snow"),
    80: ("Rain showers", "rain"), 81: ("Rain showers", "rain"), 82: ("Violent showers", "rain"),
    85: ("Snow showers", "snow"), 86: ("Snow showers", "snow"),
    95: ("Thunderstorm", "storm"), 96: ("Thunderstorm with hail", "storm"), 99: ("Thunderstorm with hail", "storm"),
}
STORM_CODES = {95, 96, 99}


class WeatherError(Exception):
    """A short, friendly message that is safe to show to a farmer."""


def describe_code(code) -> tuple:
    try:
        return _CODES.get(int(code), ("Unknown", "cloud"))
    except (TypeError, ValueError):
        return ("Unknown", "cloud")


def _get_json(url: str, params: dict, timeout: int = 20) -> dict:
    full = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full, headers={"User-Agent": "AgroNova/2.0 (student project)"})
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context(cafile=certifi.where())) as resp:  # noqa: S310 - fixed https URLs above
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_error = e
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise WeatherError("The weather service returned an unreadable answer. Please try again later.") from e
    reason = getattr(last_error, "reason", last_error)
    detail = str(reason)[:120]
    raise WeatherError("Could not reach Open-Meteo after 3 attempts. Check the app server internet access."
                       + (f" (Details: {detail})" if detail else "")) from last_error


def parse_geocode(raw: dict) -> list:
    out = []
    for r in (raw or {}).get("results") or []:
        try:
            out.append({"name": r.get("name", ""), "admin1": r.get("admin1", ""), "country": r.get("country", ""),
                        "lat": float(r["latitude"]), "lon": float(r["longitude"]), "timezone": r.get("timezone", "")})
        except (KeyError, TypeError, ValueError):
            continue
    return out


def place_label(p: dict) -> str:
    return ", ".join(x for x in (p.get("name"), p.get("admin1"), p.get("country")) if x)


def geocode(query: str, count: int = 5) -> list:
    query = (query or "").strip()
    if len(query) < 2:
        raise WeatherError("Please type the name of your village, town or district.")
    raw = _get_json(GEOCODE_URL, {"name": query, "count": count, "language": "en", "format": "json"})
    return parse_geocode(raw)


def _num(v, default=0.0):
    return default if v is None else float(v)


def normalize_forecast(raw: dict, now: datetime.datetime = None) -> dict:
    """Open-Meteo JSON -> {'fetched_at', 'timezone', 'current': {...}, 'daily': [{...}, ...]}."""
    try:
        daily_raw, cur = raw["daily"], raw.get("current") or {}
        days = []
        for i, date in enumerate(daily_raw["time"]):
            days.append({
                "date": date,
                "code": daily_raw["weather_code"][i],
                "tmax": daily_raw["temperature_2m_max"][i],
                "tmin": daily_raw["temperature_2m_min"][i],
                "rain_mm": _num(daily_raw["precipitation_sum"][i]),
                "rain_prob": _num(daily_raw.get("precipitation_probability_max", [None] * (i + 1))[i]),
                "wind_max": _num(daily_raw["wind_speed_10m_max"][i]),
            })
    except (KeyError, IndexError, TypeError) as e:
        raise WeatherError("The weather service sent an answer we could not read. Please try again later.") from e
    return {
        "fetched_at": (now or datetime.datetime.now()).isoformat(timespec="minutes"),
        "timezone": raw.get("timezone", ""),
        "current": {"temp": cur.get("temperature_2m"), "humidity": cur.get("relative_humidity_2m"),
                    "rain_mm": cur.get("precipitation"), "code": cur.get("weather_code"),
                    "wind": cur.get("wind_speed_10m")},
        "daily": days,
    }


def fetch_forecast(lat: float, lon: float, days: int = 7) -> dict:
    raw = _get_json(FORECAST_URL, {"latitude": f"{lat:.4f}", "longitude": f"{lon:.4f}", "current": CURRENT_VARS,
                                   "daily": DAILY_VARS, "timezone": "auto", "forecast_days": days})
    return normalize_forecast(raw)


def age_minutes(forecast: dict, now: datetime.datetime = None) -> float:
    try:
        fetched = datetime.datetime.fromisoformat(forecast["fetched_at"])
    except (KeyError, TypeError, ValueError):
        return float("inf")
    return ((now or datetime.datetime.now()) - fetched).total_seconds() / 60


# --------------------------------------------------------------------------- farm rules
def farm_alerts(daily: list) -> list:
    """Transparent rules (not agronomic prescriptions). Each alert: {kind, level, title, text}.

    level: 'warn' (act / be careful), 'good' (favourable), 'info'.
    """
    if not daily:
        return []
    near = daily[:3]
    today = daily[0]
    rain48 = sum(d["rain_mm"] for d in daily[:2])
    prob48 = max(d["rain_prob"] for d in daily[:2])
    rain3 = sum(d["rain_mm"] for d in near)
    alerts = []

    if any(d["code"] in STORM_CODES for d in near):
        alerts.append({"kind": "safety", "level": "warn", "title": "Thunderstorm possible",
                       "text": "Stay out of open fields during storms. Secure tools, covers and young plants."})
    if any(d["rain_mm"] >= 20 for d in near):
        alerts.append({"kind": "harvest", "level": "warn", "title": "Heavy rain expected",
                       "text": "If crops are ripe, harvest early and keep them dry. Clear drainage channels. "
                               "Delay spraying and fertilizer."})

    if rain48 >= 5 or prob48 >= 70:
        alerts.append({"kind": "water", "level": "good", "title": "Hold irrigation for now",
                       "text": "Rain looks likely in the next 2 days. Check the soil after the rain before watering."})
    elif rain3 < 2 and max(d["tmax"] for d in near) >= 32:
        alerts.append({"kind": "water", "level": "warn", "title": "Hot and dry: plan watering",
                       "text": "Little rain is expected. Water early morning or late evening, and check soil moisture first."})
    else:
        alerts.append({"kind": "water", "level": "info", "title": "Check soil before watering",
                       "text": "No strong rain signal. Push a finger 5 cm into the soil: water only if it is dry."})

    if today["wind_max"] >= 20 or today["rain_prob"] >= 60 or today["rain_mm"] >= 2:
        alerts.append({"kind": "spray", "level": "warn", "title": "Avoid spraying today",
                       "text": "Wind or rain can carry spray away or wash it off. Wait for a calm, dry spell."})
    else:
        alerts.append({"kind": "spray", "level": "good", "title": "Good window for spraying",
                       "text": "Low wind and little rain. Spray in the early morning and follow the product label."})

    if any(d["tmax"] is not None and d["tmax"] >= 38 for d in near):
        alerts.append({"kind": "heat", "level": "warn", "title": "Heat stress risk",
                       "text": "Water in the cool hours, mulch the soil, and avoid heavy field work at midday."})
    if any(d["tmin"] is not None and d["tmin"] <= 2 for d in near):
        alerts.append({"kind": "frost", "level": "warn", "title": "Frost risk",
                       "text": "Cover seedlings and tender plants in the evening. Water the soil lightly before a cold night."})
    if all(d["rain_mm"] < 2 and d["rain_prob"] < 40 for d in near) and not any(a["kind"] == "harvest" for a in alerts):
        alerts.append({"kind": "harvest", "level": "good", "title": "Dry spell: good for harvest and drying",
                       "text": "If your crop is ready, the next 3 days look dry enough to harvest and dry it."})
    return alerts


def forecast_for_prompt(forecast: dict, place: str = "") -> str:
    """The forecast as plain text for Gemini. Metric numbers; the style rules tell it which units to write."""
    cur, lines = forecast.get("current") or {}, []
    where = place or "the farmer's location"
    head = f"LIVE FORECAST from Open-Meteo for {where} (fetched {forecast.get('fetched_at', '?')})."
    lines.append(head)
    if cur.get("temp") is not None:
        lines.append(f"Now: {cur['temp']} C, humidity {cur.get('humidity')}%, wind {cur.get('wind')} km/h, "
                     f"{describe_code(cur.get('code'))[0]}.")
    for d in forecast.get("daily", []):
        lines.append(f"{d['date']}: {describe_code(d['code'])[0]}, {d['tmin']} to {d['tmax']} C, rain {d['rain_mm']} mm "
                     f"(chance {d['rain_prob']:.0f}%), wind up to {d['wind_max']} km/h")
    return "\n".join(lines)


def rain_summary(forecast: dict, days: int = 3) -> str:
    """One short line for the journal / dashboard, e.g. '31 C, rain 0 mm today'."""
    d = (forecast.get("daily") or [None])[0]
    cur = forecast.get("current") or {}
    if not d:
        return ""
    temp = cur.get("temp") if cur.get("temp") is not None else d["tmax"]
    return f"{temp:.0f} C, {describe_code(d['code'])[0].lower()}, rain {d['rain_mm']:.1f} mm today"
