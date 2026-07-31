"""Tools the ReAct agent can call. Plain functions + OpenAI-style schemas."""

import os

import requests
from dotenv import load_dotenv

import net  # noqa: F401  - patches urllib3 to skip the blackholed IPv6 route

load_dotenv()

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TAVILY_URL = "https://api.tavily.com/search"


def geocode(city, state=""):
    """City name -> lat/lon using Open-Meteo's free geocoding API (no key needed)."""
    resp = requests.get(
        GEOCODE_URL,
        params={"name": city, "count": 5, "country": "IN", "language": "en"},
        timeout=20,
    )
    resp.raise_for_status()
    results = resp.json().get("results") or []
    if not results:
        return {"error": f"Could not find a place called '{city}' in India."}

    # Prefer the hit whose admin1 (state) matches what the farmer picked.
    match = next(
        (r for r in results if state and state.lower() in (r.get("admin1") or "").lower()),
        results[0],
    )
    return {
        "lat": match["latitude"],
        "lon": match["longitude"],
        "resolved_name": f"{match['name']}, {match.get('admin1', '')}",
    }


def get_weather(city, state=""):
    """Current conditions + next 12 hours for a location. Free, no API key."""
    place = geocode(city, state)
    if "error" in place:
        return place

    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": place["lat"],
            "longitude": place["lon"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,is_day",
            "hourly": "precipitation_probability,wind_speed_10m,temperature_2m",
            "forecast_days": 2,
            "timezone": "auto",
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    hourly = data["hourly"]
    current = data["current"]

    # The hourly array starts at midnight, so skip to the current hour first.
    now_hour = current["time"][:13]
    start = next((i for i, t in enumerate(hourly["time"]) if t[:13] >= now_hour), 0)

    # Trim to the next 12 hours so the agent's context stays small.
    forecast = [
        {
            "time": hourly["time"][i],
            "rain_chance_percent": hourly["precipitation_probability"][i],
            "wind_kmh": hourly["wind_speed_10m"][i],
            "temp_c": hourly["temperature_2m"][i],
        }
        for i in range(start, min(start + 12, len(hourly["time"])))
    ]

    return {
        "location": place["resolved_name"],
        "current": {
            "local_time": current["time"],
            "is_daylight": bool(current["is_day"]),
            "temp_c": current["temperature_2m"],
            "humidity_percent": current["relative_humidity_2m"],
            "wind_kmh": current["wind_speed_10m"],
            "precipitation_mm": current["precipitation"],
        },
        "next_12_hours": forecast,
    }


# Agronomy advice must come from extension services, not blogs or product sellers.
# We append this server-side so the agent cannot search unrestricted.
TRUSTED_SOURCES = (
    "India dosage per litre site:icar.org.in OR site:tnau.ac.in OR site:ppqs.gov.in "
    "OR site:gov.in OR site:edu"
)


def web_search(query):
    """Tavily search for chemical/dosage details, restricted to trusted agronomic sources."""
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return {"note": "web search unavailable (no TAVILY_API_KEY) - use the organic fallback"}

    resp = requests.post(
        TAVILY_URL,
        json={
            "api_key": key,
            "query": f"{query} {TRUSTED_SOURCES}",
            "max_results": 3,
            "search_depth": "basic",
        },
        timeout=30,
    )
    resp.raise_for_status()
    results = [
        {"title": r["title"], "url": r["url"], "content": r["content"]}
        for r in resp.json().get("results", [])
    ]
    if not results:
        return {"note": "no trusted sources found for this query - use the organic fallback"}
    return results


TOOLS = {"get_weather": get_weather, "web_search": web_search}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get current weather and the next 12 hours of forecast (wind speed, rain "
                "probability, temperature) for a city in India. Call this before recommending "
                "when to spray."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City or town name"},
                    "state": {"type": "string", "description": "Indian state name"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search university and government agricultural extension sources for treatment "
                "details: the recommended chemical, dosage per litre, and pre-harvest interval. "
                "Results are automatically restricted to trusted .edu/.gov agronomic sources, so "
                "just describe what you need in plain terms."
            ),
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
]
