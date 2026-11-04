"""Market Prices: official mandi prices where available (India, free key) or prices you type in, plus a simple
"which crop may pay better" comparison that only uses numbers entered by the farmer."""
import datetime

import pandas as pd
import streamlit as st

from utils import market, store, ui, units
from utils.gemini import secret
from views import shared as sh


def _delete_price(price_id: str) -> None:
    store.delete_by_id(sh.farm()["prices"], price_id)


def _live_prices() -> None:
    p = sh.profile()
    if p["country"] in market.EU_MEMBER_STATES:
        _eu_prices(p)
        return
    key = str(secret("DATA_GOV_IN_API_KEY", "") or "").strip()
    if p["country"] != "India":
        st.info("Official live prices are available for India only. For other countries, type the prices you see in your "
                "local market in the next tab.")
        return
    if not key:
        st.info("To see official mandi prices, add a free **DATA_GOV_IN_API_KEY** (from data.gov.in) to the app secrets. "
                "Until then, type prices from your market in the next tab.")
        return
    with st.form("mandi_form"):
        c1, c2 = st.columns(2)
        state = c1.text_input("State", value=p["region"], placeholder="e.g. Tamil Nadu")
        commodity = c2.text_input("Crop (optional)", placeholder="e.g. Tomato")
        go_fetch = st.form_submit_button("Show prices", type="primary")
    if go_fetch:
        try:
            with st.spinner("Fetching prices..."):
                st.session_state["mandi"] = market.fetch_agmarknet(key, state.strip(), commodity.strip().title())
        except market.MarketError as e:
            st.error(str(e))
    rows = st.session_state.get("mandi")
    if rows is not None:
        if not rows:
            st.warning("No prices found for this search. Try a different spelling or leave the crop empty.")
        else:
            st.caption("Prices are in Rs per quintal (100 kg), from the Government of India open data portal. Latest date available per market.")
            st.dataframe(pd.DataFrame(market.summarize(rows)).rename(columns={
                "commodity": "Crop", "markets": "Markets", "avg_modal": "Typical price (modal)", "lowest": "Lowest", "highest": "Highest"}),
                hide_index=True)
            with st.expander("See each market"):
                st.dataframe(pd.DataFrame(rows)[["market", "district", "commodity", "variety", "date", "min", "max", "modal"]],
                             hide_index=True)


def _eu_prices(profile: dict) -> None:
    st.caption("Official weekly cereal market prices reported to the European Commission. Prices are shown in the source currency and unit; availability and latest week vary by country and cereal.")
    with st.form("eu_cereal_prices_form"):
        country = st.selectbox("EU member country", list(market.EU_MEMBER_STATES),
                               index=list(market.EU_MEMBER_STATES).index(profile["country"]))
        days = st.selectbox("Recent period", [90, 180, 365], format_func=lambda d: {90: "Last 3 months", 180: "Last 6 months", 365: "Last year"}[d])
        fetch = st.form_submit_button("Show official prices", type="primary")
    if fetch:
        try:
            with st.spinner("Fetching official prices..."):
                st.session_state["eu_cereal_prices"] = market.fetch_eu_cereal_prices(country, days)
                st.session_state["eu_cereal_country"] = country
        except market.MarketError as e:
            st.error(str(e))
    rows = st.session_state.get("eu_cereal_prices")
    if rows is not None and st.session_state.get("eu_cereal_country") == country:
        if not rows:
            st.info("The European Commission has no cereal prices for this country and period. Try a longer period or another EU country.")
        else:
            shown = [{"Country": r["country"], "Cereal": r["commodity"], "Market": r["market"], "Stage": r["stage"],
                      "Period": " – ".join(x for x in (r["date"], r["end_date"]) if x),
                      "Price": r["price"], "Unit": r["unit"]} for r in rows]
            st.dataframe(pd.DataFrame(shown), hide_index=True, use_container_width=True)
            st.caption("Source: European Commission Agri-food Data Portal. These are reported market reference prices, not a guaranteed local farmgate offer.")
            st.link_button("Open the official EU market data", "https://agridata.ec.europa.eu/extensions/dataportal/agricultural_markets.html")


def _my_prices() -> None:
    farm, pr = sh.farm(), sh.prefs()
    crops = [c["name"] for c in sh.profile()["crops"]]
    with st.form("price_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        crop = c1.text_input("Crop *", placeholder=crops[0] if crops else "e.g. tomato")
        place = c2.text_input("Market or buyer", placeholder="e.g. town market")
        c3, c4, c5 = st.columns(3)
        price = c3.number_input("Price *", min_value=0.0, value=0.0, step=1.0)
        unit = c4.selectbox("Per", market.PRICE_UNITS, index=1 if units.weight_label(pr["units"]) == "quintal" else 0)
        day = c5.date_input("Date seen", value=sh.today())
        add = st.form_submit_button("Save price", type="primary")
    if add:
        if not crop.strip() or price <= 0:
            st.error("Please enter the crop and a price above zero.")
        else:
            farm["prices"].insert(0, {"id": store.new_id(), "crop": crop.strip()[:60], "market": place.strip()[:60],
                                      "price": price, "unit": unit, "date": day.isoformat()})
            st.rerun()
    if not farm["prices"]:
        st.markdown(ui.empty_html("No prices saved", "Type what buyers are paying near you. AgroNova never invents prices."),
                    unsafe_allow_html=True)
        return
    st.dataframe(pd.DataFrame(farm["prices"]).drop(columns=["id"]).rename(columns=str.title), hide_index=True)
    with st.expander("Remove a price"):
        for item in farm["prices"][:15]:
            st.button(f"Remove {item['crop']} {item['price']:g} {item['unit']} ({item['date']})", key=f"rmp_{item['id']}",
                      on_click=_delete_price, args=(item["id"],))


def _compare() -> None:
    pr = sh.prefs()
    area = units.area_label(pr["units"])
    st.markdown(f"Compare crops for **one {area}**. Use the **same unit** for the price and the yield "
                f"(for example price per kg and yield in kg).")
    if "cmp_df" not in st.session_state:
        names = [c["name"] for c in sh.profile()["crops"]][:4] or ["", ""]
        latest = {}
        for item in reversed(sh.farm()["prices"]):
            latest[item["crop"].lower()] = item["price"]
        nan = float("nan")
        st.session_state["cmp_df"] = pd.DataFrame(
            [{"Crop": n, "Price per unit": latest.get(n.lower(), nan), f"Yield per {area}": nan, f"Cost per {area}": nan} for n in names])
    number = st.column_config.NumberColumn(min_value=0.0)
    edited = st.data_editor(st.session_state["cmp_df"], num_rows="dynamic", hide_index=True, key="cmp_editor",
                            column_config={"Price per unit": number, f"Yield per {area}": number, f"Cost per {area}": number})
    rows = [{"crop": r.get("Crop"), "price": r.get("Price per unit"), "yield_per_area": r.get(f"Yield per {area}"),
             "cost_per_area": r.get(f"Cost per {area}")} for r in edited.to_dict("records")]
    result = market.margin_table(rows)
    if not result:
        st.caption("Fill in at least one full row (crop, price, yield and cost) to see the comparison.")
        return
    df = pd.DataFrame(result).rename(columns={"crop": "Crop", "revenue": "Money in", "cost": "Money out",
                                              "margin": "Left over", "margin_pct": "Return %"})
    st.dataframe(df, hide_index=True)
    st.bar_chart(df.set_index("Crop")["Left over"])
    st.markdown(ui.callout_html("This is simple arithmetic on the numbers you typed. It ignores price changes, bad weather, "
                                "labour and selling costs. Use it to start a conversation with a buyer or adviser, not to decide alone."),
                unsafe_allow_html=True)
    if st.button("Ask Novi to comment on this comparison", key="cmp_ai"):
        table = "; ".join(f"{r['crop']}: income {r['revenue']}, cost {r['cost']}, left over {r['margin']}" for r in result)
        ctx = {"Crop comparison (numbers entered by the farmer, per " + area + ")": table, **sh.farm_context()}
        text, links = sh.run_ai(sh.build_prompt("market", ctx, sh.forecast_extra()))
        if text:
            sh.save_result("market", "Which crop to grow?", text, links, country=sh.profile()["country"])
    res = st.session_state["results"].get("market")
    if res:
        sh.render_result(res["text"])
        sh.advice_tools("market", res["text"], res["time"], res.get("links"), res.get("country", ""))


def page_market() -> None:
    sh.page_header("market", "Market Prices", "See what crops sell for near you, and compare what may be worth growing.")
    t1, t2, t3 = st.tabs(["Official prices", "My prices", "Compare crops"])
    with t1:
        _live_prices()
    with t2:
        _my_prices()
    with t3:
        _compare()
    with st.expander("Where to check prices"):
        from utils import sources
        st.markdown(ui.sources_html(sources.links_for(sh.profile()["country"], sh.profile()["region"], "market")), unsafe_allow_html=True)
