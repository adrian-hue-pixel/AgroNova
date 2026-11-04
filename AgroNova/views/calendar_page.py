"""Crop Calendar: what to do next by crop and growth stage, with reminders (in the app and as a phone-calendar file)."""
import datetime

import streamlit as st

from utils import farmcal, prompts, ui, weather
from utils.gemini import GeminiError, generate_json
from views import shared as sh

WEATHER_KINDS = {"water": ("water", "heat", "frost"), "harvest": ("harvest",), "scout": ("spray",), "fertilize": ("spray", "harvest"),
                 "weed": ("spray",), "plant": ("water",)}


def _toggle(task_id: str) -> None:
    for t in sh.farm()["tasks"]:
        if t.get("id") == task_id:
            t["done"] = bool(st.session_state.get(f"cal_{task_id}", False))


def _clear_done() -> None:
    t = sh.farm()["tasks"]
    t[:] = [x for x in t if not x.get("done")]


def _build(crop: str, planted: datetime.date, maturity, use_ai: bool) -> None:
    tasks = []
    if use_ai:
        ph = sh.loader(("Novi is planning your season...", "Choosing the right moments..."))
        try:
            prompt = prompts.build_calendar_prompt(crop, sh.profile()["region"], planted.isoformat(),
                                                   maturity or farmcal.match_template(crop)["maturity"])
            tasks = farmcal.tasks_from_ai(generate_json(prompt), crop, planted)
        except GeminiError as e:
            st.warning(f"{e} Using the built-in calendar instead.")
        ph.empty()
    if not tasks:
        tasks = farmcal.build_schedule(crop, planted, maturity)
    farm = sh.farm()
    farm["tasks"][:] = [t for t in farm["tasks"] if not (t.get("crop") == crop and not t.get("done"))]
    farm["tasks"].extend(tasks)
    # keep the crop's planting date in the profile so the stage bar is right
    for c in sh.profile()["crops"]:
        if c["name"].lower() == crop.lower():
            c["planted"], c["maturity"] = planted.isoformat(), maturity
    st.session_state["cal_msg"] = f"Calendar ready: {len(tasks)} tasks for {crop}."


def _task_row(t: dict, today: datetime.date) -> None:
    due = farmcal.parse_date(t.get("due"))
    when = due.strftime("%a %d %b") if due else "no date"
    label = f"{when}: {t.get('crop', '')}. {t.get('title', '')}  [{farmcal.KIND_LABELS.get(t.get('kind'), 'Task')}]"
    st.checkbox(label, key=f"cal_{t['id']}", value=bool(t.get("done")), on_change=_toggle, args=(t["id"],))


def page_calendar() -> None:
    sh.page_header("calendar", "Crop Calendar", "See what to do next for each crop, and get reminders.")
    farm, p, today = sh.farm(), sh.profile(), sh.today()
    if st.session_state.get("cal_msg"):
        st.success(st.session_state.pop("cal_msg"))

    # ---- where each crop is now
    st.markdown(ui.heading("Where my crops are"), unsafe_allow_html=True)
    if not p["crops"]:
        st.markdown(ui.empty_html("No crops yet", "Add a crop below, or in My Farm."), unsafe_allow_html=True)
    for c in p["crops"]:
        prog = farmcal.crop_progress(c, today)
        nxt = farmcal.next_task_for(farm["tasks"], c["name"], today)
        sub = f"Next: {nxt['title']} ({nxt['due']})" if nxt else "No pending tasks"
        if prog["days_to_harvest"] is not None:
            sub += f" · about {prog['days_to_harvest']} days to harvest" if prog["days_to_harvest"] > 0 else " · harvest time"
        st.markdown(ui.crop_progress_html(c["name"], prog["stage"], prog["pct"], sub), unsafe_allow_html=True)

    # ---- build / rebuild
    with st.expander("Add a crop or rebuild its calendar", expanded=not farm["tasks"]):
        names = [c["name"] for c in p["crops"]]
        with st.form("cal_form"):
            pick = st.selectbox("Crop", names + ["Another crop..."]) if names else "Another crop..."
            other = st.text_input("Crop name (if another crop)", placeholder="e.g. groundnut")
            c1, c2 = st.columns(2)
            planted = c1.date_input("Planting date", value=today)
            days = c2.number_input("Days from planting to harvest (0 = typical)", min_value=0, max_value=400, value=0, step=5)
            use_ai = st.checkbox("Let Novi tailor the calendar to my region (uses AI)", value=False)
            go_build = st.form_submit_button("Build calendar", type="primary")
        if go_build:
            crop = (other.strip() if pick == "Another crop..." else pick).strip()
            if not crop:
                st.error("Please choose or type a crop.")
            else:
                if not any(c["name"].lower() == crop.lower() for c in p["crops"]):
                    p["crops"].append({"name": crop[:60], "planted": planted.isoformat(), "area": "", "maturity": int(days) or None})
                _build(crop[:60], planted, int(days) or None, use_ai)
                st.rerun()
        st.caption("Built-in calendars are general guides for common crops. Sowing windows and varieties differ by region, "
                   "so confirm dates with your local agriculture office or KVK.")

    groups = farmcal.categorize(farm["tasks"], today)

    # ---- weather check for this week's tasks
    fc = farm.get("weather")
    upcoming = groups["overdue"] + groups["today"] + groups["week"]
    if fc and upcoming:
        wanted = {k for t in upcoming for k in WEATHER_KINDS.get(t.get("kind"), ())} | {"safety"}
        hints = [a for a in weather.farm_alerts(fc["daily"]) if a["kind"] in wanted]
        if hints:
            st.markdown(ui.heading("Weather check for your tasks"), unsafe_allow_html=True)
            st.markdown(ui.alerts_html(hints), unsafe_allow_html=True)

    # ---- the task list
    st.markdown(ui.heading("My tasks"), unsafe_allow_html=True)
    if not farm["tasks"]:
        st.markdown(ui.empty_html("No tasks yet", "Build a calendar above to see what to do and when."), unsafe_allow_html=True)
    for key, title, kind in (("overdue", "Overdue", "bad"), ("today", "Today", "today"), ("week", "Next 7 days", ""), ("later", "Later", "")):
        if groups[key]:
            st.markdown(ui.group_heading(title, kind), unsafe_allow_html=True)
            for t in groups[key][:40]:
                _task_row(t, today)
    if groups["done"]:
        with st.expander(f"Finished tasks ({len(groups['done'])})"):
            for t in groups["done"]:
                _task_row(t, today)
            st.button("Clear finished tasks", on_click=_clear_done, key="cal_clear")

    # ---- own task + reminders
    with st.expander("Add my own task"):
        with st.form("own_task", clear_on_submit=True):
            title = st.text_input("What needs to be done? *")
            c1, c2 = st.columns(2)
            crop = c1.text_input("Crop (optional)")
            due = c2.date_input("Date", value=today)
            if st.form_submit_button("Add task") and title.strip():
                farm["tasks"].append({"id": farmcal.new_id(), "crop": crop.strip()[:60], "title": title.strip()[:140],
                                      "kind": "other", "due": due.isoformat(), "done": False})
                st.rerun()
    pending = [t for t in farm["tasks"] if not t.get("done")]
    if pending:
        st.download_button("Download reminders for my phone calendar (.ics)", farmcal.make_ics(pending, p.get("name") or "My farm"),
                           file_name="agronova_calendar.ics", mime="text/calendar", key="dl_ics")
        st.caption("Open the file on your phone and choose 'Add to calendar'. Your phone will remind you at 7 am on each day, "
                   "even when AgroNova is closed.")
