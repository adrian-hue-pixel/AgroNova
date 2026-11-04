"""Measurement units: what the farmer sees on screen and what Gemini is told to use.

The weather service and all stored numbers are METRIC. These helpers only change how numbers are shown
and what we ask the model to write, so nothing stored ever needs converting back.
"""

UNIT_SYSTEMS = {
    "Metric (hectare, kg, °C, mm)": {
        "short": "Metric", "temp": "C", "rain": "mm", "wind": "kmh", "area": "hectare", "weight": "kg",
        "prompt": "Use metric units: hectares, kilograms, degrees Celsius, millimetres of rain, km/h.",
    },
    "India (acre, quintal, °C, mm)": {
        "short": "India", "temp": "C", "rain": "mm", "wind": "kmh", "area": "acre", "weight": "quintal",
        "prompt": "Use units common in Indian farming: acres, quintals (100 kg), degrees Celsius, millimetres of rain, km/h.",
    },
    "Imperial (acre, lb, °F, inch)": {
        "short": "Imperial", "temp": "F", "rain": "in", "wind": "mph", "area": "acre", "weight": "lb",
        "prompt": "Use imperial units: acres, pounds, degrees Fahrenheit, inches of rain, mph.",
    },
}
DEFAULT_UNITS = next(iter(UNIT_SYSTEMS))


def system(name: str) -> dict:
    return UNIT_SYSTEMS.get(name) or UNIT_SYSTEMS[DEFAULT_UNITS]


def temp(c, units: str) -> str:
    if c is None:
        return "-"
    if system(units)["temp"] == "F":
        return f"{c * 9 / 5 + 32:.0f}°F"
    return f"{c:.0f}°C"


def rain(mm, units: str) -> str:
    if mm is None:
        return "-"
    if system(units)["rain"] == "in":
        return f"{mm / 25.4:.2f} in"
    return f"{mm:.0f} mm" if mm >= 10 else f"{mm:.1f} mm"


def wind(kmh, units: str) -> str:
    if kmh is None:
        return "-"
    if system(units)["wind"] == "mph":
        return f"{kmh * 0.621371:.0f} mph"
    return f"{kmh:.0f} km/h"


def area_label(units: str) -> str:
    return system(units)["area"]


def weight_label(units: str) -> str:
    return system(units)["weight"]


def prompt_rule(units: str) -> str:
    return system(units)["prompt"]
