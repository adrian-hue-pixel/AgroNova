"""Home page and the farmer's Dashboard: weather, active crops, upcoming tasks and recent advice at a glance."""
import streamlit as st

from utils import farmcal, ui
from views import forecast as fcv
from views import shared as sh

# (page, icon key, title, tagline)
TOOLS = [
    ("forecast", "forecast", "Live Weather", "Your forecast, with watering, spraying and harvest hints."),
    ("doctor", "doctor", "Plant Doctor", "Upload a leaf photo and answer a few questions."),
    ("ask", "ask", "Ask by Voice", "Speak your question and listen to the answer."),
    ("calendar", "calendar", "Crop Calendar", "What to do next, with reminders."),
    ("crop", "crop", "Crop choices", "Which crops suit your land, season and water."),
    ("market", "market", "Market Prices", "Compare what may be worth growing."),
    ("journal", "journal", "Farm Journal", "Plantings, photos, treatments and harvests."),
    ("soil", "soil", "Soil & Fertilizer", "Check your soil and how to improve it."),
    ("sustainable", "sustainable", "Sustainable Farming", "Save water, protect soil, use fewer chemicals."),
]


def tool_card(page: str, icon_key: str, title: str, tagline: str, prefix: str) -> None:
    with st.container(key=f"fcard_{prefix}{page}"):
        st.markdown(ui.feature_card_html(icon_key, title, tagline), unsafe_allow_html=True)
        st.button("Open  \u203a", key=f"open_{prefix}{page}", on_click=sh.go, args=(page,))


def tool_grid(prefix: str, tools=TOOLS, per_row: int = 3) -> None:
    for i in range(0, len(tools), per_row):
        for col, t in zip(st.columns(per_row, gap="medium"), tools[i:i + per_row]):
            with col:
                tool_card(*t, prefix)


def page_home() -> None:
    st.markdown(ui.hero_html(len(sh.LANGUAGES), sh.greeting()), unsafe_allow_html=True)
    _, c1, c2, _ = st.columns([2, 1.2, 1.2, 2])
    c1.button("Open my dashboard", on_click=sh.go, args=("dashboard",), type="primary", key="cta_dash")
    c2.button("Set up My Farm", on_click=sh.go, args=("farm",), key="cta_lab")
    st.markdown(ui.steps_html(), unsafe_allow_html=True)
    st.markdown(ui.heading("Everything your farm needs"), unsafe_allow_html=True)
    tool_grid("h_")


def _mark_done(task_id: str) -> None:
    for t in sh.farm()["tasks"]:
        if t.get("id") == task_id:
            t["done"] = True


def page_dashboard() -> None:
    sh.page_header("dashboard", "My Dashboard", f"{sh.greeting()}. Here is your farm today.")
    farm, p, today = sh.farm(), sh.profile(), sh.today()
    groups = farmcal.categorize(farm["tasks"], today)
    due_now = len(groups["overdue"]) + len(groups["today"])
    s1, s2, s3 = st.columns(3, gap="medium")
    s1.markdown(ui.stat_html(len(p["crops"]), "Active crops", "", .1), unsafe_allow_html=True)
    s2.markdown(ui.stat_html(due_now, "Tasks due now", "", .2), unsafe_allow_html=True)
    s3.markdown(ui.stat_html(len(farm["advice"]), "Saved answers", "", .3), unsafe_allow_html=True)

    # ---- weather
    st.markdown(ui.heading("Weather"), unsafe_allow_html=True)
    if not sh.has_location():
        st.markdown(ui.empty_html("Add your farm location", "Then your forecast and weather hints appear here."), unsafe_allow_html=True)
        st.button("Choose my location", on_click=sh.go, args=("forecast",), key="dash_loc")
    else:
        fc, err = sh.get_forecast()
        if err:
            st.warning(err)
        if fc:
            fcv.show_forecast(fc, compact=True)
            st.button("See the full 7-day forecast", on_click=sh.go, args=("forecast",), key="dash_fc")

    # ---- crops
    st.markdown(ui.heading("My crops"), unsafe_allow_html=True)
    if not p["crops"]:
        st.markdown(ui.empty_html("No crops yet", "Add the crops you grow to see how they are growing."), unsafe_allow_html=True)
        st.button("Add my crops", on_click=sh.go, args=("farm",), key="dash_crops")
    for c in p["crops"]:
        prog = farmcal.crop_progress(c, today)
        nxt = farmcal.next_task_for(farm["tasks"], c["name"], today)
        sub = f"Next: {nxt['title']} ({nxt['due']})" if nxt else "No pending tasks"
        st.markdown(ui.crop_progress_html(c["name"], prog["stage"], prog["pct"], sub), unsafe_allow_html=True)

    # ---- tasks
    st.markdown(ui.heading("Coming up"), unsafe_allow_html=True)
    shown = groups["overdue"] + groups["today"] + groups["week"]
    if not shown:
        st.markdown(ui.empty_html("Nothing due this week", "Build a crop calendar to get reminders."), unsafe_allow_html=True)
        st.button("Open crop calendar", on_click=sh.go, args=("calendar",), key="dash_cal")
    for t in shown[:6]:
        due = farmcal.parse_date(t.get("due"))
        late = "  (overdue)" if due and due < today else ""
        st.checkbox(f"{due.strftime('%a %d %b') if due else ''}: {t.get('crop', '')}. {t['title']}{late}",
                    key=f"dash_t_{t['id']}", on_change=_mark_done, args=(t["id"],))

    # ---- recent advice
    st.markdown(ui.heading("Recent advice"), unsafe_allow_html=True)
    if not farm["advice"]:
        st.markdown(ui.empty_html("No advice yet", "Ask Novi something. Your answers are kept here."), unsafe_allow_html=True)
    for a in farm["advice"][:3]:
        st.markdown(ui.advice_row_html(a["title"], a["time"].replace("T", " "), a["language"]), unsafe_allow_html=True)
    if farm["advice"]:
        st.button("Open guides and saved advice", on_click=sh.go, args=("guides",), key="dash_guides")

    st.markdown(ui.heading("Quick tools"), unsafe_allow_html=True)
    tool_grid("d_", TOOLS[:3])
