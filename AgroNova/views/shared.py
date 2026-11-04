"""State, constants and helpers shared by every page."""
import datetime
import hashlib

import streamlit as st
import streamlit.components.v1 as components

from utils import helpers, prompts, sources, store, ui, units, voice, weather
from utils.gemini import GeminiError, generate_advice, generate_with_sources, has_api_key, secret

EU_COUNTRIES = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia",
                "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania",
                "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
                "Spain", "Sweden"]
COUNTRIES = ["India", "Ghana", "Canada", "Kenya", "Brazil", *EU_COUNTRIES, "Other"]
LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam", "Marathi", "Bengali",
             "French", "Spanish", "Portuguese", "Twi (Ghana)"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]
SOILS = ["Not sure", "Sandy", "Loamy", "Clay", "Silty", "Red / laterite", "Black (cotton) soil", "Peaty / organic"]
WATER = ["Very low (rain only, frequent dry spells)", "Moderate", "Good (irrigation available)"]
PREF_KEYS = ("language", "units", "detail", "large_text", "low_data", "dark_mode")


# ---------------------------------------------------------------- state
def farm() -> dict:
    return st.session_state["farm"]


def profile() -> dict:
    return farm()["profile"]


def prefs() -> dict:
    s = st.session_state
    return {"language": s.get("language", "English"), "units": s.get("units", units.DEFAULT_UNITS),
            "detail": s.get("detail", prompts.DEFAULT_DETAIL), "large_text": bool(s.get("large_text", False)),
            "low_data": bool(s.get("low_data", False)), "dark": bool(s.get("dark_mode", False))}


def apply_prefs(saved: dict) -> None:
    """Copy saved preferences into widget state. Call only BEFORE the widgets are drawn (or in a callback)."""
    s = st.session_state
    if saved.get("language") in LANGUAGES:
        s["language"] = saved["language"]
    if saved.get("units") in units.UNIT_SYSTEMS:
        s["units"] = saved["units"]
    if saved.get("detail") in prompts.DETAIL_LEVELS:
        s["detail"] = saved["detail"]
    for key in ("large_text", "low_data", "dark_mode"):
        if key in saved:
            s[key] = bool(saved[key])


def local_save_enabled() -> bool:
    return str(secret("LOCAL_SAVE", "")).strip().lower() in ("1", "true", "yes")


def ensure_state() -> None:
    s = st.session_state
    if "farm" not in s:
        loaded = store.load_local() if local_save_enabled() else None
        s["farm"] = loaded or store.new_farm()
        apply_prefs(s["farm"].get("prefs", {}))
    s.setdefault("dark_mode", False)
    s.setdefault("page", "home")
    s.setdefault("results", {})
    s.setdefault("feedback", [])
    s.setdefault("validation_log", [])
    s.setdefault("question_count", 0)
    s.setdefault("lab_run_id", 0)
    s.setdefault("profile_version", 0)


def autosave() -> None:
    """Keep preferences inside the farm data, and write the local file when LOCAL_SAVE is on."""
    farm()["prefs"] = {"language": prefs()["language"], "units": prefs()["units"], "detail": prefs()["detail"],
                       "large_text": prefs()["large_text"], "low_data": prefs()["low_data"], "dark_mode": prefs()["dark"]}
    if local_save_enabled():
        digest = hashlib.md5(store.to_json(farm()).encode("utf-8")).hexdigest()  # noqa: S324 - change detection only
        if st.session_state.get("_saved_hash") != digest and store.save_local(farm()):
            st.session_state["_saved_hash"] = digest


def go(page: str) -> None:
    """Button callback: change the page (runs before the next rerun, so it is safe to set the widget key)."""
    st.session_state["page"] = page


def today() -> datetime.date:
    return datetime.date.today()


def greeting() -> str:
    hour = datetime.datetime.now().hour
    name = (profile().get("name") or "").strip().split(" ")[0] if "farm" in st.session_state else ""
    who = name or "farmer"
    return f"Good morning, {who}" if hour < 12 else f"Good afternoon, {who}" if hour < 18 else f"Good evening, {who}"


# ---------------------------------------------------------------- farm context for prompts
def farm_context() -> dict:
    p = profile()
    crops = ", ".join(c["name"] for c in p["crops"])
    return {"Country": p["country"], "Region": p["region"], "Soil type": "" if p["soil"] == "Not sure" else p["soil"],
            "Soil pH": p["ph"], "Water availability": p["water"], "Farm size": p["land_size"], "Crops currently grown": crops}


def place_text() -> str:
    p = profile()
    return p.get("place") or ", ".join(x for x in (p.get("region"), p.get("country")) if x)


# ---------------------------------------------------------------- weather
@st.cache_data(ttl=1800, show_spinner=False)
def _cached_forecast(lat: float, lon: float) -> dict:
    return weather.fetch_forecast(lat, lon)


def has_location() -> bool:
    p = profile()
    return p.get("lat") is not None and p.get("lon") is not None


def get_forecast(force: bool = False) -> tuple:
    """Returns (forecast or None, error message or None). Falls back to the last saved forecast if offline."""
    f, p = farm(), profile()
    saved = f.get("weather")
    if not has_location():
        return None, None
    if saved and not force and (prefs()["low_data"] or weather.age_minutes(saved) < 30):
        return saved, None
    if force:
        getattr(_cached_forecast, "clear", lambda: None)()
    try:
        fc = _cached_forecast(float(p["lat"]), float(p["lon"]))
    except weather.WeatherError as e:
        return saved, str(e)
    f["weather"] = fc
    return fc, None


def forecast_extra() -> str:
    fc = farm().get("weather")
    return weather.forecast_for_prompt(fc, place_text()) if fc else ""


def location_picker(prefix: str) -> None:
    """Search a place name and save its coordinates (used on My Farm and Live Weather)."""
    p = profile()
    if has_location():
        st.caption(f"Weather location: {p.get('place') or 'saved'}  ({float(p['lat']):.2f}, {float(p['lon']):.2f})")
    q = st.text_input("Search your village, town or district", key=f"{prefix}_geo_q", placeholder="e.g. Madurai, Kumasi, Nakuru")
    if st.button("Search place", key=f"{prefix}_geo_btn"):
        try:
            st.session_state[f"{prefix}_geo"] = weather.geocode(q)
            if not st.session_state[f"{prefix}_geo"]:
                st.warning("No place found. Try a bigger nearby town or check the spelling.")
        except weather.WeatherError as e:
            st.error(str(e))
    results = st.session_state.get(f"{prefix}_geo") or []
    if results:
        labels = [weather.place_label(r) for r in results]
        choice = st.selectbox("Choose the right place", labels, key=f"{prefix}_geo_pick")
        if st.button("Use this location", key=f"{prefix}_geo_use", type="primary"):
            r = results[labels.index(choice)]
            p.update({"lat": r["lat"], "lon": r["lon"], "place": choice, "timezone": r["timezone"]})
            farm()["weather"] = None
            st.session_state[f"{prefix}_geo"] = []
            st.rerun()


# ---------------------------------------------------------------- AI calls
def loader(messages=("Novi is thinking about your farm...", "Checking farming knowledge...", "Writing simple advice for you...")):
    ph = st.empty()
    ph.markdown(ui.loader_html(messages), unsafe_allow_html=True)
    return ph


def run_ai(prompt: str, *, images=None, grounded: bool = False, messages=None) -> tuple:
    """Call Gemini with a friendly loader. Returns (text, links) or (None, []) after showing a friendly error."""
    if not has_api_key():
        st.error("The Gemini API key is not configured yet. See the README (API key configuration).")
        return None, []
    ph = loader(messages) if messages else loader()
    try:
        if grounded:
            text, links = generate_with_sources(prompt)
        else:
            text, links = generate_advice(prompt, images=images), []
    except GeminiError as e:
        ph.empty()
        st.error(str(e))
        return None, []
    ph.empty()
    return text, links


def build_prompt(feature: str, context: dict, extra: str = "") -> str:
    pr = prefs()
    return prompts.build_prompt_v2(feature, context, pr["language"], pr["detail"], units.prompt_rule(pr["units"]), extra)


def save_result(feature: str, title: str, text: str, links: list = None, **extra) -> None:
    st.session_state["results"][feature] = dict({"text": text, "time": datetime.datetime.now().isoformat(),
                                                 "links": links or []}, **extra)
    store.add_advice(farm(), feature, title, text, prefs()["language"], links)
    st.session_state["question_count"] += 1


# ---------------------------------------------------------------- showing results
def render_result(text: str) -> None:
    """Show Gemini's answer as clear section cards instead of one long paragraph."""
    sections = helpers.parse_sections(text)
    if not sections:  # the model ignored the format: still show the answer
        st.markdown(text)
        return
    layout = [("sec_0", "Overview", "Overview"), ("sec_1", "Recommended actions", "Recommended Actions"),
              ("sec_2", "Why these recommendations?", "Why These Recommendations"), ("sec_3", "Precautions", "Precautions")]
    for box, title, name in layout:
        with st.container(key=box):
            st.markdown(ui.section_title("", title), unsafe_allow_html=True)
            st.markdown(sections[name])
    with st.container(key="sec_4"):
        st.markdown(ui.section_title("", "More ideas and follow-up questions"), unsafe_allow_html=True)
        st.markdown(sections["Additional Suggestions"])
    st.success("Remember: this is general guidance. Please confirm important decisions with your local agricultural officer.")


def advice_tools(feature: str, text: str, token: str, extra_links: list = None, country: str = "") -> None:
    """Listen / download / sources, shown under every piece of advice."""
    pr = prefs()
    c1, c2 = st.columns([2, 1])
    with c1:
        components.html(voice.speak_html(text, pr["language"], dark=pr["dark"]), height=96)
    with c2:
        st.download_button("Download this advice", text, file_name=f"agronova_{feature}.md", key=f"dl_{feature}_{token}")
    with st.expander("Advice sources: where to check this"):
        links = sources.links_for(country or profile().get("country", ""), profile().get("region", ""), feature)
        st.markdown(ui.sources_html(links), unsafe_allow_html=True)
        st.caption("These are official portals for your country and topic. AgroNova cannot confirm that a page repeats the "
                   "AI's exact words, so use them to check the advice and learn more.")
        if extra_links:
            found = [{"name": l["title"], "url": l["url"], "why": "Found by Gemini web search"} for l in extra_links]
            st.markdown(ui.sources_html(found, "Pages Gemini found on the web (please check them yourself)"), unsafe_allow_html=True)


def page_header(page: str, title: str, tagline: str, bubble: str = "") -> None:
    st.markdown(ui.page_header(page, "", title, tagline, bubble), unsafe_allow_html=True)


def needs_profile_hint() -> None:
    if not (profile().get("region") or profile().get("crops")):
        st.info("Tip: save your farm once in **My Farm** and AgroNova will use it in every answer.")
        st.button("Set up My Farm", on_click=go, args=("farm",), key=f"hint_farm_{st.session_state['page']}")
