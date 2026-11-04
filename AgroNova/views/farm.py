"""My Farm: save the profile once (place, soil, water, crops) so every page can use it."""
import datetime

import streamlit as st

from utils import farmcal, helpers, store, ui, units
from views import shared as sh


def _remove_crop(index: int) -> None:
    crops = sh.profile()["crops"]
    if 0 <= index < len(crops):
        name = crops[index]["name"]
        crops.pop(index)
        t = sh.farm()["tasks"]
        t[:] = [x for x in t if not (x.get("crop") == name and not x.get("done"))]


def page_farm() -> None:
    sh.page_header("farm", "My Farm", "Tell AgroNova about your farm once. It remembers, so you never type it again.")
    tab_place, tab_farm, tab_crops, tab_save = st.tabs(["1. Weather place", "2. My land", "3. My crops", "4. Keep my data"])
    p = sh.profile()
    pr = sh.prefs()

    with tab_place:
        st.markdown("Search for the village or town closest to your farm. AgroNova uses it for the **live weather forecast**.")
        sh.location_picker("farm")

    with tab_farm:
        with st.form("profile_form"):
            name = st.text_input("Your name or farm name (optional)", value=p["name"])
            c1, c2 = st.columns(2)
            country = c1.selectbox("Country", sh.COUNTRIES, index=sh.COUNTRIES.index(p["country"]) if p["country"] in sh.COUNTRIES else 0)
            region = c2.text_input("State / region / district", value=p["region"], placeholder="e.g. Tamil Nadu")
            c3, c4 = st.columns(2)
            soil = c3.selectbox("Soil type", sh.SOILS, index=sh.SOILS.index(p["soil"]) if p["soil"] in sh.SOILS else 0)
            water = c4.selectbox("Water availability", sh.WATER, index=sh.WATER.index(p["water"]) if p["water"] in sh.WATER else 1)
            c5, c6 = st.columns(2)
            ph = c5.text_input("Soil pH (optional)", value=p["ph"], placeholder="e.g. 6.5")
            size = c6.text_input(f"Farm size in {units.area_label(pr['units'])}s (optional)", value=p["land_size"], placeholder="e.g. 2.5")
            saved = st.form_submit_button("Save my farm", type="primary")
        if saved:
            if ph.strip() and helpers.parse_ph(ph) is None:
                st.error("Soil pH must be a number between 0 and 14 (for example 6.5).")
            else:
                p.update({"name": name.strip(), "country": country, "region": region.strip(), "soil": soil, "water": water,
                          "ph": ph.strip(), "land_size": size.strip()})
                st.session_state["profile_version"] += 1   # forms re-fill from the new profile
                st.success("Saved. AgroNova will now use these details in your advice.")

    with tab_crops:
        st.markdown("Add each crop you grow. AgroNova can build a **crop calendar** with reminders for you.")
        with st.form("crop_form", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            cname = cc1.text_input("Crop name *", placeholder="e.g. paddy, tomato, maize")
            planted = cc2.date_input("Planting date", value=sh.today())
            cc3, cc4 = st.columns(2)
            area = cc3.text_input("Area (optional)", placeholder=f"e.g. 1.5 {units.area_label(pr['units'])}")
            days = cc4.number_input("Days from planting to harvest (0 = typical)", min_value=0, max_value=400, value=0, step=5)
            make_cal = st.checkbox("Build the crop calendar for this crop now", value=True)
            add = st.form_submit_button("Add crop", type="primary")
        if add:
            if not cname.strip():
                st.error("Please type the crop name.")
            else:
                crop = {"name": cname.strip()[:60], "planted": planted.isoformat(), "area": area.strip()[:40],
                        "maturity": int(days) or None}
                p["crops"].append(crop)
                if make_cal:
                    sh.farm()["tasks"].extend(farmcal.build_schedule(crop["name"], planted, crop["maturity"]))
                st.session_state["profile_version"] += 1
                st.rerun()

        if not p["crops"]:
            st.markdown(ui.empty_html("No crops yet", "Add your first crop above."), unsafe_allow_html=True)
        for i, c in enumerate(p["crops"]):
            prog = farmcal.crop_progress(c, sh.today())
            sub = f"Planted {prog['planted']}" if prog["planted"] else "Planting date not set"
            if c.get("area"):
                sub += f" · {c['area']}"
            st.markdown(ui.crop_progress_html(c["name"], prog["stage"], prog["pct"], sub), unsafe_allow_html=True)
            st.button(f"Remove {c['name']}", key=f"rm_crop_{i}", on_click=_remove_crop, args=(i,))

    with tab_save:
        st.markdown("**Your data stays with you.** AgroNova does not need an account. To keep your farm between visits, "
                    "download your farm file now and load it from the sidebar next time.")
        st.download_button("Download my farm file", store.to_json(sh.farm()), file_name="agronova_farm.json",
                           mime="application/json", key="dl_farm_file")
        st.caption("The file holds your profile, crops, calendar, journal (with small photos) and saved advice. Keep it private.")
        if sh.local_save_enabled():
            st.success("Automatic saving on this device is ON (LOCAL_SAVE). Your data is also saved to data/farm_data.json.")
        else:
            st.caption("Automatic saving is off. It is meant for one device only (see README: LOCAL_SAVE).")
        st.divider()
        sure = st.checkbox("I want to erase everything saved in this session", key="erase_ok")
        if st.button("Erase my farm data", disabled=not sure, key="erase_btn"):
            st.session_state["farm"] = store.new_farm()
            st.session_state["profile_version"] += 1
            st.session_state["results"] = {}
            st.rerun()
