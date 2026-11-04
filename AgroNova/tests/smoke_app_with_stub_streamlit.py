"""SMOKE TEST with a FAKE Streamlit (not the real thing).

Runs app.py top-to-bottom for every page, in several situations (just viewing, submitting every form, no API key,
a farm that already has crops / tasks / journal / forecast), using a stub Streamlit and a fake Gemini SDK.
It catches typos, NameErrors, bad dictionary keys, wrong function signatures and broken code paths.
It does NOT prove the UI looks right or that the real Streamlit API accepts every argument, and it makes NO real API
call and NO network call. Run from the project root:  python tests/smoke_app_with_stub_streamlit.py
"""
import datetime
import os
import runpy
import sys
from unittest.mock import MagicMock

import pandas as pd

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
from test_gemini_mock import install_fakes  # noqa: E402
from utils import store, weather  # noqa: E402
from utils.prompts import SECTION_TITLES  # noqa: E402

GOOD = "\n".join(f"## {t}\n- point about {t}" for t in SECTION_TITLES)
TODAY = datetime.date.today()
FORECAST = weather.normalize_forecast({
    "timezone": "Asia/Kolkata", "current": {"temperature_2m": 31, "relative_humidity_2m": 60, "precipitation": 0, "weather_code": 2, "wind_speed_10m": 9},
    "daily": {"time": [(TODAY + datetime.timedelta(days=i)).isoformat() for i in range(7)], "weather_code": [2, 63, 95, 1, 0, 3, 61],
              "temperature_2m_max": [33, 30, 29, 34, 35, 33, 31], "temperature_2m_min": [24, 23, 22, 24, 25, 24, 23],
              "precipitation_sum": [0, 8, 25, 0, 0, 1, 6], "precipitation_probability_max": [10, 80, 90, 5, 0, 20, 60],
              "wind_speed_10m_max": [12, 18, 30, 10, 9, 14, 16]}})


def rich_farm():
    farm = store.new_farm()
    farm["profile"].update({"name": "Selvi Rajan", "country": "India", "region": "Tamil Nadu", "place": "Madurai, Tamil Nadu, India",
                            "lat": 9.9, "lon": 78.1, "soil": "Red / laterite", "water": "Moderate", "ph": "6.5", "land_size": "2",
                            "crops": [{"name": "Paddy", "planted": (TODAY - datetime.timedelta(days=40)).isoformat(), "area": "1 acre", "maturity": None},
                                      {"name": "Tomato", "planted": "", "area": "", "maturity": 100}]})
    from utils import farmcal
    farm["tasks"] = farmcal.build_schedule("Paddy", TODAY - datetime.timedelta(days=40))
    farm["tasks"][0]["done"] = True
    store.add_advice(farm, "crop", "Crop advice", GOOD, "English", [])
    store.add_advice(farm, "ask", "Plain answer", "no sections here", "English", [])
    store.add_journal(farm, {"date": TODAY.isoformat(), "crop": "Paddy", "kind": "Harvest", "note": "first cut", "treatment": "neem",
                             "weather": "31 C", "qty": 120.0, "qty_unit": "kg", "cost": 300.0, "photo": ""})
    store.add_journal(farm, {"date": "bad-date", "crop": "", "kind": "Observation", "note": "<b>x</b>", "qty": "", "cost": ""})
    farm["prices"] = [{"id": "p1", "crop": "Tomato", "market": "Town", "price": 22.0, "unit": "per kg", "date": TODAY.isoformat()}]
    farm["weather"] = FORECAST
    return farm


def run(page, submit=False, key_present=True, rich=False, extra_state=None, farm=None):
    _, _, _ = install_fakes()
    st = MagicMock()
    st.secrets = {"GEMINI_API_KEY": "k"} if key_present else {}
    st.cache_resource = lambda *a, **k: (lambda f: f)
    st.cache_data = lambda *a, **k: (lambda f: f)
    state = {"page": page, "language": "Hindi", "feedback": [{"time": "t", "feature": "crop", "rating": 5, "language": "Hindi", "comment": "=bad()"}]}
    if rich:
        state["farm"] = farm or rich_farm()
    state.update(extra_state or {})
    st.session_state = state
    st.columns.side_effect = lambda spec, **k: [st for _ in range(spec if isinstance(spec, int) else len(spec))]
    st.tabs.side_effect = lambda labels, **k: [st for _ in labels]
    st.selectbox.side_effect = lambda label, options, **k: options[0]
    st.multiselect.side_effect = lambda label, options, **k: list(options)[:1]
    st.radio.side_effect = lambda label, options, **k: options[0]
    st.slider.side_effect = lambda label, lo, hi, val, *a, **k: val
    st.data_editor.side_effect = lambda df, **k: df
    st.text_input.return_value = "Tamil Nadu" if submit else ""
    st.text_area.return_value = "yellow leaves" if submit else ""
    st.number_input.return_value = 5.0 if submit else 0.0
    st.date_input.return_value = TODAY
    st.checkbox.return_value = True
    st.toggle.return_value = False
    st.file_uploader.return_value = None
    st.audio_input.return_value = None
    st.button.return_value = submit
    st.form_submit_button.return_value = submit
    components = MagicMock()
    st.components = components
    sys.modules.update({"streamlit": st, "streamlit.components": components, "streamlit.components.v1": components.v1})
    for name in [m for m in sys.modules if m == "utils.gemini" or m.startswith("views")]:
        sys.modules.pop(name)
    import utils.gemini as g
    g.generate_advice = lambda *a, **k: GOOD
    g.generate_with_sources = lambda *a, **k: (GOOD, [{"title": "Page", "url": "https://example.org/x"}])
    g.generate_json = lambda *a, **k: [{"question": "Where did it start?", "options": ["Bottom", "Top", "Not sure"]}]
    g.transcribe_audio = lambda *a, **k: "when to sow paddy"
    g.has_api_key = lambda: key_present
    runpy.run_path("app.py", run_name="__main__")
    return st


PAGES = ["home", "dashboard", "farm", "forecast", "doctor", "ask", "calendar", "market", "journal", "crop", "soil", "sustainable",
         "pest", "weather", "guides", "lab", "about"]
SCENARIOS = {
    "view": dict(),
    "submit": dict(submit=True),
    "no_key": dict(key_present=False),
    "rich": dict(rich=True),
    "rich_submit": dict(rich=True, submit=True),
    "dark_large_lowdata": dict(rich=True, extra_state={"dark_mode": True, "large_text": True, "low_data": True}),
    "imperial_detailed": dict(rich=True, extra_state={"units": "Imperial (acre, lb, °F, inch)", "detail": "Detailed", "language": "Tamil"}),
}
EXTRA_RUNS = [   # (label, page, kwargs)
    ("doctor questions stage", "doctor", dict(rich=True, submit=True, extra_state={"doctor": {
        "stage": "questions", "crop": "tomato", "parts": "Leaves", "symptoms": "spots", "treat": "Both - show me options", "photo": b"x", "mime": "image/jpeg",
        "questions": [{"question": "Where?", "options": ["a", "b"]}], "journaled": False, "run": "r1"}})),
    ("doctor result stage", "doctor", dict(rich=True, extra_state={"doctor": {"stage": "result", "crop": "tomato", "parts": "Leaves", "symptoms": "spots",
                                                                           "photo": None, "journaled": False, "run": "r1"}, "results": {"doctor": {"text": GOOD, "time": "t", "links": []}}})),
    ("ask with a recording", "ask", dict(rich=True, submit=True)),
    ("forecast with a cached result", "forecast", dict(rich=True, submit=True, extra_state={"results": {"forecast": {"text": GOOD, "time": "t", "links": [{"title": "T", "url": "https://x.org"}]}}})),
    ("market compare results", "market", dict(rich=True, submit=True, extra_state={"cmp_df": pd.DataFrame([
        {"Crop": "Tomato", "Price per unit": 20.0, "Yield per acre": 8000.0, "Cost per acre": 90000.0}]), "mandi": [
        {"market": "A", "district": "D", "state": "S", "commodity": "Tomato", "variety": "", "date": "d", "min": 1.0, "max": 2.0, "modal": 1.5}]})),
    ("old weather forecast (stale cache)", "dashboard", dict(rich=True, farm=None)),
]

failures = 0
for scenario, kw in SCENARIOS.items():
    for p in PAGES:
        try:
            run(p, **kw)
            print(f"PASS  {scenario:20} {p}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            import traceback
            print(f"FAIL  {scenario:20} {p}: {type(e).__name__}: {e}")
            traceback.print_exc(limit=-3)
for label, p, kw in EXTRA_RUNS:
    try:
        run(p, **kw)
        print(f"PASS  {label:28} {p}")
    except Exception as e:  # noqa: BLE001
        failures += 1
        import traceback
        print(f"FAIL  {label:28} {p}: {type(e).__name__}: {e}")
        traceback.print_exc(limit=-3)
print("\nFAILURES:", failures)
for leftover in ("data/feedback.csv", "data/farm_data.json"):
    if os.path.exists(leftover):
        os.remove(leftover)
sys.exit(1 if failures else 0)
