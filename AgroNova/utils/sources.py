"""Trusted agricultural guidance links shown beside every recommendation.

HONESTY NOTE: these are hand-picked official portals (stable home pages), chosen by country and topic. They are
where a farmer can verify and learn more - AgroNova cannot confirm that a particular page repeats the AI's exact
sentence. Gemini web-search links (when the farmer turns that on) are listed separately and labelled as such.
"""

GLOBAL = {
    "general": [("FAO - Food and Agriculture Organization", "https://www.fao.org/", "Global reports and farming guidance")],
    "pest": [("CABI PlantwisePlus Knowledge Bank", "https://plantwiseplusknowledgebank.org/", "Pest and disease factsheets for many crops")],
    "soil": [("FAO Global Soil Partnership", "https://www.fao.org/global-soil-partnership/en/", "Soil health and fertilizer guidance")],
    "market": [("World Bank - Agriculture", "https://www.worldbank.org/en/topic/agriculture", "Agriculture and food markets overview")],
    "weather": [("Open-Meteo", "https://open-meteo.com/", "Source of the forecast shown in AgroNova")],
}

BY_COUNTRY = {
    "India": {
        "general": [("ICAR - Indian Council of Agricultural Research", "https://icar.org.in/", "National research and advisories"),
                    ("Krishi Vigyan Kendra (KVK) portal", "https://kvk.icar.gov.in/", "Find your district KVK for local advice"),
                    ("NMSA - National Mission for Sustainable Agriculture", "https://nmsa.dac.gov.in/", "Sustainable farming programmes")],
        "soil": [("Soil Health Card portal", "https://soilhealth.dac.gov.in/", "Soil test results and crop-wise nutrient advice")],
        "weather": [("India Meteorological Department (IMD)", "https://mausam.imd.gov.in/", "Official forecasts and warnings")],
        "market": [("Agmarknet", "https://agmarknet.gov.in/", "Official mandi prices"),
                   ("e-NAM", "https://enam.gov.in/", "National agriculture market")],
    },
    "Ghana": {
        "general": [("Ministry of Food and Agriculture (MoFA)", "https://mofa.gov.gh/", "Extension services and programmes")],
        "weather": [("Ghana Meteorological Agency", "https://www.meteo.gov.gh/", "Official forecasts")],
    },
    "Canada": {
        "general": [("Agriculture and Agri-Food Canada", "https://agriculture.canada.ca/", "Federal agriculture information")],
        "weather": [("Environment Canada - Weather", "https://weather.gc.ca/", "Official forecasts and warnings")],
    },
    "Kenya": {
        "general": [("KALRO - Kenya Agricultural and Livestock Research", "https://www.kalro.org/", "Research and crop guides"),
                    ("Ministry of Agriculture (Kilimo)", "https://kilimo.go.ke/", "Policy and extension")],
        "weather": [("Kenya Meteorological Department", "https://meteo.go.ke/", "Official forecasts")],
    },
    "Brazil": {
        "general": [("Embrapa", "https://www.embrapa.br/", "Brazilian agricultural research")],
        "weather": [("INMET", "https://portal.inmet.gov.br/", "Official forecasts")],
    },
    "Italy": {"general": [("CREA - Council for Agricultural Research", "https://www.crea.gov.it/", "Italian agricultural research")]},
}
# Regional extras (matched on the region text, case-insensitive)
BY_REGION = {"tamil": [("Tamil Nadu Agricultural University - Agritech Portal", "https://agritech.tnau.ac.in/",
                        "Crop production guides for Tamil Nadu")]}

TOPIC_OF_FEATURE = {"crop": "general", "pest": "pest", "doctor": "pest", "weather": "weather", "forecast": "weather",
                    "soil": "soil", "sustainable": "general", "market": "market", "calendar": "general", "ask": "general"}


def links_for(country: str, region: str = "", feature: str = "general") -> list:
    """Return [{'name', 'url', 'why'}] - country-specific first, then topic links, then global ones. No duplicates."""
    topic = TOPIC_OF_FEATURE.get(feature, feature if feature in GLOBAL else "general")
    entries = []
    country_links = BY_COUNTRY.get(country, {})
    for t in (topic, "general"):
        entries += country_links.get(t, [])
    for key, extra in BY_REGION.items():
        if key in (region or "").lower() and country == "India":
            entries += extra
    entries += GLOBAL.get(topic, [])
    if topic != "general":
        entries += GLOBAL["general"]
    seen, out = set(), []
    for name, url, why in entries:
        if url not in seen:
            seen.add(url)
            out.append({"name": name, "url": url, "why": why})
    return out[:6]
