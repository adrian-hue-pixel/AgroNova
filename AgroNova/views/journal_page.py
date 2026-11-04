"""Farm Journal: planting dates, photos, weather, treatments and harvest results in one timeline."""
import datetime

import pandas as pd
import streamlit as st

from utils import store, ui, weather
from views import shared as sh

KINDS = ["Planting", "Watering", "Fertilizing", "Weeding", "Pest or disease", "Treatment", "Observation", "Harvest", "Expense", "Sale"]
QTY_UNITS = ["kg", "quintal", "tonne", "lb", "bags", "pieces"]


def _delete(entry_id: str) -> None:
    store.delete_by_id(sh.farm()["journal"], entry_id)


def page_journal() -> None:
    sh.page_header("journal", "Farm Journal", "Record what happens on your farm, so you can learn from every season.")
    farm, p = sh.farm(), sh.profile()
    crops = [c["name"] for c in p["crops"]]

    with st.expander("Add a journal entry", expanded=not farm["journal"]):
        with st.form("journal_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            day = c1.date_input("Date", value=sh.today())
            crop = c2.selectbox("Crop", crops + ["Whole farm / other"]) if crops else c2.text_input("Crop", placeholder="e.g. paddy")
            kind = c3.selectbox("What happened?", KINDS)
            note = st.text_area("Notes", placeholder="e.g. Planted 2 acres of paddy after the first rain.", max_chars=600, height=90)
            treatment = st.text_input("Treatment or inputs used (optional)", placeholder="e.g. neem spray, compost")
            c4, c5, c6 = st.columns(3)
            qty = c4.number_input("Harvest amount (if any)", min_value=0.0, value=0.0, step=1.0)
            qty_unit = c5.selectbox("Unit", QTY_UNITS)
            cost = c6.number_input("Money spent or earned (optional)", min_value=0.0, value=0.0, step=10.0)
            photo = st.file_uploader("Photo (optional)", type=["jpg", "jpeg", "png", "webp"], key="journal_photo")
            add_weather = st.checkbox("Add today's weather from my forecast", value=bool(farm.get("weather")))
            save = st.form_submit_button("Save entry", type="primary")
        if save:
            if not note.strip() and photo is None and kind != "Harvest":
                st.error("Please write a short note or add a photo.")
            else:
                thumb = ""
                if photo is not None:
                    try:
                        thumb = store.make_thumbnail(photo.getvalue())
                    except ValueError as e:
                        st.error(str(e))
                        thumb = None
                if thumb is not None:
                    fc = farm.get("weather")
                    store.add_journal(farm, {"date": day.isoformat(), "crop": crop if isinstance(crop, str) else "", "kind": kind,
                                             "note": note.strip(), "treatment": treatment.strip(),
                                             "weather": weather.rain_summary(fc) if (add_weather and fc) else "",
                                             "qty": qty if qty > 0 else "", "qty_unit": qty_unit if qty > 0 else "",
                                             "cost": cost if cost > 0 else "", "photo": thumb})
                    st.success("Saved in your journal.")
                    st.rerun()

    # ---- harvest summary
    totals = store.harvest_totals(farm["journal"])
    if totals:
        st.markdown(ui.heading("Harvest so far"), unsafe_allow_html=True)
        cols = st.columns(min(3, len(totals)))
        for col, (crop_name, by_unit) in zip(cols * 3, totals.items()):
            col.metric(crop_name, " + ".join(f"{v:g} {u}" for u, v in by_unit.items()))

    # ---- timeline
    st.markdown(ui.heading("My journal"), unsafe_allow_html=True)
    entries = farm["journal"]
    filt = st.selectbox("Show", ["All crops"] + sorted({e.get("crop", "") for e in entries if e.get("crop")}), key="jr_filter")
    shown = [e for e in sorted(entries, key=lambda e: e.get("date", ""), reverse=True) if filt == "All crops" or e.get("crop") == filt]
    if not shown:
        st.markdown(ui.empty_html("Nothing here yet", "Add your first entry: a planting date, a photo, or a harvest."), unsafe_allow_html=True)
    for e in shown[:60]:
        d = None
        try:
            d = datetime.date.fromisoformat(e.get("date", ""))
        except ValueError:
            pass
        bits = []
        if e.get("treatment"):
            bits.append(f"Used: {e['treatment']}")
        if e.get("weather"):
            bits.append(e["weather"])
        if e.get("qty") not in ("", None):
            bits.append(f"{e['qty']:g} {e.get('qty_unit', '')}")
        if e.get("cost") not in ("", None):
            bits.append(f"Money: {e['cost']:g}")
        meta = " · ".join(bits)
        st.markdown(ui.journal_item_html(str(d.day) if d else "?", d.strftime("%b %Y") if d else "", e.get("kind", ""),
                                         e.get("crop", ""), e.get("note", ""), meta), unsafe_allow_html=True)
        if e.get("photo"):
            st.image(store.thumbnail_bytes(e["photo"]), width=180)
        st.button("Delete this entry", key=f"jr_del_{e['id']}", on_click=_delete, args=(e["id"],))

    if entries:
        csv = pd.DataFrame(store.journal_csv_rows(entries)).to_csv(index=False)
        st.download_button("Download my journal (CSV)", csv, file_name="agronova_journal.csv", mime="text/csv", key="dl_journal")
