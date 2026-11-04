"""Live Weather & Alerts: the forecast for the farm, with watering / spraying / harvest hints and AI advice."""
import datetime

import streamlit as st

from utils import ui, units, weather
from views import advice_forms
from views import shared as sh


def weekday_label(date_str: str, index: int) -> str:
    if index == 0:
        return "Today"
    try:
        return datetime.date.fromisoformat(date_str).strftime("%a %d")
    except ValueError:
        return date_str[5:]


def strip_days(fc: dict, unit_name: str) -> list:
    out = []
    for i, d in enumerate(fc["daily"]):
        label, icon_key = weather.describe_code(d["code"])
        out.append({"label": weekday_label(d["date"], i), "icon": icon_key, "hi": units.temp(d["tmax"], unit_name),
                    "lo": units.temp(d["tmin"], unit_name), "rain": units.rain(d["rain_mm"], unit_name),
                    "prob": f"{d['rain_prob']:.0f}%"})
    return out


def show_forecast(fc: dict, compact: bool = False) -> list:
    """Draw the weather card, 7-day strip and alerts. Returns the alerts."""
    pr = sh.prefs()
    cur, un = fc.get("current") or {}, pr["units"]
    today_d = fc["daily"][0]
    desc, icon_key = weather.describe_code(cur.get("code") if cur.get("code") is not None else today_d["code"])
    facts = [f"High {units.temp(today_d['tmax'], un)} · Low {units.temp(today_d['tmin'], un)}",
             f"Rain today {units.rain(today_d['rain_mm'], un)} ({today_d['rain_prob']:.0f}%)",
             f"Wind {units.wind(cur.get('wind') if cur.get('wind') is not None else today_d['wind_max'], un)}"]
    if cur.get("humidity") is not None:
        facts.append(f"Humidity {cur['humidity']:.0f}%")
    temp_now = cur.get("temp") if cur.get("temp") is not None else today_d["tmax"]
    st.markdown(ui.weather_hero_html(sh.place_text(), units.temp(temp_now, un), desc, icon_key, facts,
                                     f"Updated {fc.get('fetched_at', '')[:16].replace('T', ' ')}"), unsafe_allow_html=True)
    alerts = weather.farm_alerts(fc["daily"])
    if compact:
        st.markdown(ui.alerts_html(alerts[:2]), unsafe_allow_html=True)
        return alerts
    st.markdown(ui.heading("Next 7 days"), unsafe_allow_html=True)
    st.markdown(ui.forecast_strip_html(strip_days(fc, un)), unsafe_allow_html=True)
    st.markdown(ui.heading("What this means for your farm"), unsafe_allow_html=True)
    st.markdown(ui.alerts_html(alerts), unsafe_allow_html=True)
    st.caption("These hints come from simple weather rules, not from AI. They are general; check your crop's needs. "
               + weather.ATTRIBUTION)
    return alerts


def page_forecast() -> None:
    sh.page_header("forecast", "Live Weather & Alerts", "The forecast for your farm, turned into watering, spraying and harvest advice.")
    pr = sh.prefs()
    if not sh.has_location():
        st.markdown(ui.empty_html("Where is your farm?", "Search for your village or town to see the live forecast."),
                    unsafe_allow_html=True)
        sh.location_picker("fc")
    else:
        c1, c2 = st.columns([1, 1])
        refresh = c1.button("Refresh forecast", key="fc_refresh")
        with c2.expander("Change location"):
            sh.location_picker("fc")
        fc, err = sh.get_forecast(force=refresh)
        if err:
            st.warning(err)
        if fc:
            show_forecast(fc)
            st.divider()
            st.subheader("Get advice for this forecast")
            crops = ", ".join(c["name"] for c in sh.profile()["crops"]) or "your crops"
            st.caption(f"Novi will use this forecast and your farm details ({crops}).")
            grounded = False
            if not pr["low_data"]:
                grounded = st.checkbox("Also check Google Search for web sources (uses a little more data)", key="fc_ground")
            if st.button("Plan my week", type="primary", key="fc_plan"):
                ctx = sh.farm_context()
                prompt = sh.build_prompt("forecast", ctx, sh.forecast_extra())
                text, links = sh.run_ai(prompt, grounded=grounded)
                if text:
                    sh.save_result("forecast", "Weather plan for the week", text, links, country=sh.profile()["country"])
            res = st.session_state["results"].get("forecast")
            if res:
                st.info("**Based on the live forecast above** (Open-Meteo) and your farm details.")
                sh.render_result(res["text"])
                sh.advice_tools("forecast", res["text"], res["time"], res.get("links"), res.get("country", ""))
        elif not err:
            st.info("No forecast yet. Press Refresh forecast.")

    with st.expander("No internet forecast, or no location? Describe the weather yourself"):
        advice_forms.feature_form("weather", embedded=True)
