"""AgroNova - Smart Farming Assistant (Streamlit + Google Gemini).

Run locally:  streamlit run app.py
Pages live in the views/ folder; all logic that does not need Streamlit lives in utils/ (and is unit-tested).
"""
import streamlit as st

from utils import prompts, store, ui, units
from utils.gemini import active_model, has_api_key

st.set_page_config(page_title="AgroNova - Smart Farming Assistant", page_icon="\U0001F33F", layout="wide")

from views import shared as sh  # noqa: E402  (imported after set_page_config so Streamlit stays happy)
from views.advice_forms import FEATURES, feature_form  # noqa: E402
from views.ask import page_ask  # noqa: E402
from views.calendar_page import page_calendar  # noqa: E402
from views.dashboard import page_dashboard, page_home  # noqa: E402
from views.doctor import page_doctor  # noqa: E402
from views.farm import page_farm  # noqa: E402
from views.forecast import page_forecast  # noqa: E402
from views.guides_page import page_guides  # noqa: E402
from views.journal_page import page_journal  # noqa: E402
from views.lab_about import page_about, page_lab  # noqa: E402
from views.market_page import page_market  # noqa: E402

sh.ensure_state()
pr = sh.prefs()

# ---------------------------------------------------------------- styling (light is the default)
st.markdown(ui.global_css(pr["dark"], pr["large_text"], pr["low_data"]) + ui.background_fx(pr["dark"], low_data=pr["low_data"]),
            unsafe_allow_html=True)

# ---------------------------------------------------------------- routing table
PAGE_LABELS = {
    "home": "Home", "dashboard": "My Dashboard", "farm": "My Farm", "forecast": "Live Weather & Alerts",
    "doctor": "Plant Doctor", "ask": "Ask by Voice", "calendar": "Crop Calendar", "market": "Market Prices",
    "journal": "Farm Journal", "crop": FEATURES["crop"]["title"], "soil": FEATURES["soil"]["title"],
    "sustainable": FEATURES["sustainable"]["title"], "pest": FEATURES["pest"]["title"] + " (text)",
    "weather": FEATURES["weather"]["title"] + " (your weather)",
    "guides": "Guides & Offline", "lab": "Validation Lab", "about": "About & Safety",
}
PAGES = list(PAGE_LABELS)
ROUTES = {"home": page_home, "dashboard": page_dashboard, "farm": page_farm, "forecast": page_forecast, "doctor": page_doctor,
          "ask": page_ask, "calendar": page_calendar, "market": page_market, "journal": page_journal, "guides": page_guides,
          "lab": page_lab, "about": page_about}


def load_farm_file() -> None:
    """Callback for the sidebar uploader: replace the current farm data with the uploaded file."""
    up = st.session_state.get("farm_upload")
    if up is None:
        return
    try:
        farm = store.from_json(up.getvalue().decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        st.session_state["farm_msg"] = ("error", str(e) if isinstance(e, ValueError) else "This file could not be read.")
        return
    st.session_state["farm"] = farm
    sh.apply_prefs(farm.get("prefs", {}))
    st.session_state["profile_version"] += 1
    st.session_state["results"] = {}
    st.session_state["farm_msg"] = ("success", "Your farm was loaded.")


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(ui.sidebar_brand(), unsafe_allow_html=True)
    st.radio("Menu", PAGES, key="page", format_func=PAGE_LABELS.get, label_visibility="collapsed")
    with st.expander("My farm file"):
        st.file_uploader("Load my saved farm", type=["json"], key="farm_upload", on_change=load_farm_file)
        msg = st.session_state.pop("farm_msg", None)
        if msg:
            (st.success if msg[0] == "success" else st.error)(msg[1])
        st.download_button("Save my farm", store.to_json(sh.farm()), file_name="agronova_farm.json", mime="application/json",
                           key="dl_farm_sidebar")
    with st.expander("Language, units and comfort", expanded=False):
        st.selectbox("Language of the answers", sh.LANGUAGES, key="language")
        if st.session_state["language"] != "English":
            st.caption("AI translations can contain mistakes, especially for less common languages. Please double-check.")
        st.selectbox("Units", list(units.UNIT_SYSTEMS), key="units")
        st.selectbox("How much detail?", list(prompts.DETAIL_LEVELS), key="detail")
        st.toggle("Large text", key="large_text")
        st.toggle("Low-data mode", key="low_data", help="No web font, no animation, smaller photos, no web-search extras.")
        st.toggle("Dark appearance", key="dark_mode")
    if has_api_key():
        st.success(f"API key found\nModel: {active_model()}")
    else:
        st.error("API key missing. See README.")
    st.caption("AI advice is general guidance. Confirm with local experts.")

# ---------------------------------------------------------------- page
page = st.session_state["page"]
if page in FEATURES:                      # crop / pest / weather (typed) / soil / sustainable forms
    feature_form(page)
else:
    ROUTES.get(page, page_home)()

sh.autosave()
