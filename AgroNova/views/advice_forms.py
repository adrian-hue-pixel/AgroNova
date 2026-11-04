"""The question forms (crop, pest, weather typed by hand, soil, sustainable), now pre-filled from the farm profile."""
import datetime

import streamlit as st

from utils import helpers, store, ui
from utils.gemini import has_api_key
from views import shared as sh
from views.shared import COUNTRIES, MONTHS, SOILS, WATER  # noqa: F401  (used by the field definitions below)
import csv
from pathlib import Path
from utils.helpers import safe_csv_cell

FEEDBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "feedback.csv"
NO_WEATHER_INFO = "I do not know the weather"
WEATHER_SOURCES = ["I checked a weather app or forecast", "A radio broadcast or extension officer told me",
                   "I observed it myself (sky, wind, rain)", NO_WEATHER_INFO]

# Each feature = a form. Adding or changing a field only needs a change here.
COUNTRY = {"id": "country", "label": "Country", "type": "select", "options": COUNTRIES, "required": True}
REGION = {"id": "region", "label": "State / region / district", "type": "text", "required": True,
          "placeholder": "e.g. Tamil Nadu, Ashanti Region, Ontario"}

FEATURES = {
    "crop": {
        "title": "Crop Recommendation", "icon": "",
        "tagline": "Find out which crops suit your land, season and water.",
        "fields": [
            COUNTRY, REGION,
            {"id": "soil", "label": "Soil type", "type": "select", "options": SOILS, "required": True},
            {"id": "ph", "label": "Soil pH (optional)", "type": "ph", "placeholder": "e.g. 6.5"},
            {"id": "month", "label": "Month or planting season", "type": "select", "options": MONTHS, "required": True},
            {"id": "water", "label": "Water availability", "type": "select", "options": WATER, "required": True},
            {"id": "land", "label": "Land conditions (optional)", "type": "textarea",
             "placeholder": "e.g. small 1-acre plot, slightly sloped, close to a river"},
        ],
    },
    "pest": {
        "title": "Pest & Disease Management", "icon": "",
        "tagline": "Describe what you see on your plants and get possible causes and safe options.",
        "fields": [
            {"id": "crop", "label": "Crop name", "type": "text", "required": True, "placeholder": "e.g. tomato, maize, cotton"},
            COUNTRY, REGION,
            {"id": "symptoms", "label": "Symptoms you can see", "type": "textarea", "required": True,
             "placeholder": "e.g. leaves turning yellow from the bottom, small brown spots, holes in leaves"},
            {"id": "parts", "label": "Affected plant parts", "type": "multiselect",
             "options": ["Leaves", "Stem", "Roots", "Fruit / grain", "Flowers", "Whole plant"], "required": True},
            {"id": "treatment", "label": "Treatment preference", "type": "select",
             "options": ["Organic / natural only", "Conventional is fine", "Both - show me options"], "required": True},
        ],
    },
    "weather": {
        "title": "Weather-Based Advice", "icon": "",
        "tagline": "Tell us the weather you are seeing and get irrigation, harvest and planting advice.",
        "fields": [
            COUNTRY, REGION,
            {"id": "crop", "label": "Crop", "type": "text", "required": True, "placeholder": "e.g. rice, tomato"},
            {"id": "stage", "label": "Crop stage", "type": "select", "required": True,
             "options": ["Not planted yet", "Seedling", "Growing", "Flowering / fruiting", "Ready to harvest"]},
            {"id": "source", "label": "Where does your weather information come from?", "type": "select", "required": True,
             "options": WEATHER_SOURCES},
            {"id": "rain", "label": "Rain in the last 7 days", "type": "select",
             "options": ["No rain", "Light rain", "Moderate rain", "Heavy rain / flooding"]},
            {"id": "temp", "label": "Temperature you are seeing (optional)", "type": "text",
             "placeholder": "e.g. around 35 C in the afternoon"},
            {"id": "weather", "label": "Weather you expect in the next few days", "type": "textarea",
             "required": True, "required_unless": ("source", NO_WEATHER_INFO),
             "placeholder": "e.g. forecast app says rain on Saturday; hot and dry until then"},
        ],
    },
    "soil": {
        "title": "Soil & Fertilizer Advice", "icon": "",
        "tagline": "Check if your soil suits your crop and how to improve it.",
        "fields": [
            COUNTRY, REGION,
            {"id": "crop", "label": "Crop", "type": "text", "required": True, "placeholder": "e.g. groundnut, wheat"},
            {"id": "soil", "label": "Soil type", "type": "select", "options": SOILS, "required": True},
            {"id": "ph", "label": "Soil pH (optional)", "type": "ph", "placeholder": "e.g. 5.5"},
            {"id": "nutrients", "label": "Soil test / nutrient information (optional)", "type": "textarea",
             "placeholder": "e.g. low nitrogen, medium phosphorus (from a soil health card)"},
        ],
    },
    "sustainable": {
        "title": "Sustainable Farming", "icon": "",
        "tagline": "Practical, low-cost ways to save water, protect soil and reduce chemicals.",
        "fields": [
            COUNTRY, REGION,
            {"id": "topics", "label": "Topics you want tips on", "type": "multiselect", "required": True,
             "options": ["Water conservation", "Organic farming", "Natural pest management", "Crop rotation",
                         "Soil conservation", "General sustainable practices"]},
            {"id": "crop", "label": "Main crop(s) (optional)", "type": "text", "placeholder": "e.g. millet, vegetables"},
            {"id": "size", "label": "Farm size", "type": "select", "options": ["Small (under 2 acres)", "Medium", "Large"]},
        ],
    },
}

# the typed-weather form pre-fills nothing about the forecast; it is for people with no location or no internet
PREFILL_CROP_FIELDS = ("crop",)


def _default_for(field: dict):
    p = sh.profile()
    fid = field["id"]
    if fid == "country" and p["country"] in field.get("options", []):
        return p["country"]
    if fid == "region":
        return p["region"]
    if fid == "soil" and p["soil"] in field.get("options", []):
        return p["soil"]
    if fid == "ph":
        return p["ph"]
    if fid == "water" and p["water"] in field.get("options", []):
        return p["water"]
    if fid == "crop" and p["crops"] and field["type"] == "text":
        return p["crops"][0]["name"]
    return None


def render_field(prefix: str, f: dict):
    key = f"{prefix}_{f['id']}_{st.session_state['profile_version']}"   # new key when the profile changes -> new defaults
    label = f["label"] + (" *" if f.get("required") else "")
    kind = f["type"]
    default = _default_for(f)
    if default is not None and key not in st.session_state:
        st.session_state[key] = default
    if kind in ("text", "ph"):
        return st.text_input(label, key=key, placeholder=f.get("placeholder", ""))
    if kind == "textarea":
        return st.text_area(label, key=key, placeholder=f.get("placeholder", ""), height=100)
    if kind == "select":
        return st.selectbox(label, f["options"], key=key)
    if kind == "multiselect":
        return st.multiselect(label, f["options"], key=key)


def save_feedback(entry: dict):
    st.session_state["feedback"].append(entry)
    try:
        new_file = not FEEDBACK_FILE.exists()
        with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(entry.keys()))
            if new_file:
                writer.writeheader()
            writer.writerow({k: safe_csv_cell(v) for k, v in entry.items()})
    except OSError:
        pass  # storage can be read-only; the in-session copy is still kept


def feedback_form(feature_key: str):
    st.divider()
    st.subheader("Was this helpful?")
    done_key = f"fbdone_{feature_key}_{st.session_state['results'][feature_key]['time']}"
    if st.session_state.get(done_key):
        st.success("Thank you! Your feedback helps us improve AgroNova.")
        return
    with st.form(f"feedback_{feature_key}"):
        rating = st.radio("Your rating", [1, 2, 3, 4, 5], index=3, horizontal=True, format_func=lambda n: "\u2605" * n)
        comment = st.text_area("Suggestions or problems (optional)", max_chars=500)
        if st.form_submit_button("Submit feedback"):
            save_feedback({"time": datetime.datetime.now().isoformat(timespec="seconds"), "feature": feature_key,
                           "rating": rating, "language": sh.prefs()["language"], "comment": comment.strip()})
            st.session_state[done_key] = True
            st.rerun()


def feature_form(key: str, embedded: bool = False) -> None:
    """The form + answer for one feature. `embedded` skips the page header (used inside Live Weather)."""
    f = FEATURES[key]
    if not embedded:
        sh.page_header(key, f["title"], f["tagline"])
    if key == "weather":
        st.info("This form uses **only the weather you type**. For an automatic forecast for your farm, open "
                "**Live Weather & Alerts** in the menu.")
    if not has_api_key():
        st.error("The Gemini API key is not configured yet. See the README (API key configuration).")
    if not embedded:
        sh.needs_profile_hint()

    left, right = st.columns([1.8, 1], gap="large")
    with right:
        with st.container(key=f"aside_{key}" if embedded else "aside"):
            st.markdown(ui.aside_html(sh.prefs()["language"]), unsafe_allow_html=True)
    with left:
        with st.form(f"form_{key}"):
            values = {fld["id"]: render_field(key, fld) for fld in f["fields"]}
            grounded = False
            if not sh.prefs()["low_data"]:
                grounded = st.checkbox("Also check Google Search for web sources (uses a little more data)", key=f"ground_{key}")
            submitted = st.form_submit_button("Get advice", type="primary")

    if submitted:
        problems = helpers.validate_inputs(f["fields"], values)
        if problems:
            for p in problems:
                st.error(p)
        else:
            context = {fld["label"].replace(" (optional)", ""): (", ".join(values[fld["id"]])
                       if isinstance(values[fld["id"]], list) else str(values[fld["id"]]).strip()) for fld in f["fields"]}
            extra = sh.forecast_extra() if key in ("crop", "soil", "sustainable") else ""
            prompt = sh.build_prompt(key, context, extra)
            text, links = sh.run_ai(prompt, grounded=grounded)
            if text:
                sh.save_result(key, f["title"], text, links, source=values.get("source", ""),
                               country=values.get("country", ""))

    res = st.session_state["results"].get(key)
    if res:
        st.divider()
        if key == "weather":
            st.info(f"**Based on weather you typed** (source you stated: {res.get('source') or 'not stated'}). "
                    "Not a live forecast.")
        sh.render_result(res["text"])
        sh.advice_tools(key, res["text"], res["time"], res.get("links"), res.get("country", ""))
        feedback_form(key)
