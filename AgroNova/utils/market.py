"""Local market prices and "what might be worth growing".

Honest scope: there is no free, worldwide mandi-price API. So AgroNova supports two sources:
1. India: the Government of India "Current Daily Price of Various Commodities from Various Markets (Mandi)"
   open dataset on data.gov.in (needs a FREE API key: set DATA_GOV_IN_API_KEY in the secrets). Prices are Rs per quintal.
2. Anywhere: prices the farmer (or a co-operative / extension officer) types in from the local market.
AgroNova never invents a price. The margin comparison only uses numbers the farmer enters.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

AGMARKNET_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
PRICE_UNITS = ("per kg", "per quintal (100 kg)", "per tonne", "per lb")


class MarketError(Exception):
    """Friendly message for the farmer."""


def _f(value):
    try:
        number = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None
    return None if number != number else number      # NaN (an empty spreadsheet cell) counts as missing


def parse_agmarknet(raw: dict) -> list:
    """data.gov.in JSON -> [{market, district, state, commodity, variety, date, min, max, modal}] (Rs / quintal)."""
    out = []
    for r in (raw or {}).get("records") or []:
        if not isinstance(r, dict):
            continue
        low = {str(k).lower(): v for k, v in r.items()}
        modal, mn, mx = _f(low.get("modal_price")), _f(low.get("min_price")), _f(low.get("max_price"))
        if modal is None and mn is None and mx is None:
            continue
        out.append({"market": low.get("market", ""), "district": low.get("district", ""), "state": low.get("state", ""),
                    "commodity": low.get("commodity", ""), "variety": low.get("variety", ""),
                    "date": low.get("arrival_date", ""), "min": mn, "max": mx, "modal": modal})
    return out


def fetch_agmarknet(api_key: str, state: str = "", commodity: str = "", district: str = "", limit: int = 100) -> list:
    if not api_key:
        raise MarketError("No data.gov.in API key is set, so live mandi prices are not available. "
                          "You can still type prices from your local market below.")
    params = {"api-key": api_key, "format": "json", "limit": limit}
    if state:
        params["filters[state.keyword]"] = state
    if district:
        params["filters[district]"] = district
    if commodity:
        params["filters[commodity]"] = commodity
    url = f"{AGMARKNET_URL}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgroNova/2.0 (student project)"})
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310 - fixed https URL
            raw = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        raise MarketError("Could not reach the market price service. Please try again later or type prices yourself.") from e
    return parse_agmarknet(raw)


def summarize(records: list) -> list:
    """Per commodity across the returned markets: average modal price, lowest min, highest max, number of markets."""
    groups = {}
    for r in records:
        groups.setdefault(r["commodity"] or "Unknown", []).append(r)
    rows = []
    for name, items in groups.items():
        modals = [i["modal"] for i in items if i["modal"] is not None]
        mins = [i["min"] for i in items if i["min"] is not None]
        maxs = [i["max"] for i in items if i["max"] is not None]
        rows.append({"commodity": name, "markets": len(items),
                     "avg_modal": round(sum(modals) / len(modals), 1) if modals else None,
                     "lowest": min(mins) if mins else None, "highest": max(maxs) if maxs else None})
    return sorted(rows, key=lambda r: -(r["avg_modal"] or 0))


def margin_table(rows: list) -> list:
    """rows: [{crop, price, yield_per_area, cost_per_area}] all in the SAME unit and area.

    Returns rows with revenue, margin and margin % - sorted best first. Rows with missing numbers are skipped.
    This is simple arithmetic on the farmer's own numbers, NOT a prediction.
    """
    out = []
    for r in rows:
        price, yld, cost = _f(r.get("price")), _f(r.get("yield_per_area")), _f(r.get("cost_per_area"))
        crop = str(r.get("crop") or "").strip()
        if not crop or price is None or yld is None or cost is None or price < 0 or yld < 0 or cost < 0:
            continue
        revenue = price * yld
        margin = revenue - cost
        out.append({"crop": crop, "revenue": round(revenue, 2), "cost": round(cost, 2), "margin": round(margin, 2),
                    "margin_pct": round(margin / cost * 100, 1) if cost else None})
    return sorted(out, key=lambda r: -r["margin"])
