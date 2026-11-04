"""Guides & Offline: key guides that need no internet, saved advice, and the downloadable offline pack."""
import streamlit as st

from utils import offline, ui
from utils.guides import GUIDES
from views import shared as sh


def page_guides() -> None:
    sh.page_header("guides", "Guides & Offline", "Key farming guides and your saved advice, even when the internet is weak.")
    farm = sh.farm()

    st.markdown(ui.heading("Take AgroNova with you"), unsafe_allow_html=True)
    st.markdown("Download the **offline pack**: one file with your saved advice, upcoming tasks, the last forecast and all "
                "guides. It opens in any phone browser with **no internet and no AI call**.")
    st.download_button("Download my offline pack (HTML)", offline.build_offline_pack(farm, sh.today()),
                       file_name="agronova_offline_pack.html", mime="text/html", type="primary", key="dl_offline")
    st.caption(f"Contains {len(farm['advice'])} saved answers, {sum(1 for t in farm['tasks'] if not t.get('done'))} open tasks and "
               f"{len(GUIDES)} guides. Download it again after new advice to keep it fresh.")

    st.markdown(ui.heading("Key guides"), unsafe_allow_html=True)
    st.caption("These guides are built into the app. They load instantly and use no data.")
    for g in GUIDES.values():
        with st.expander(g["title"]):
            st.markdown("\n".join(f"{i}. {s}" for i, s in enumerate(g["steps"], 1)))

    st.markdown(ui.heading("My saved advice"), unsafe_allow_html=True)
    if not farm["advice"]:
        st.markdown(ui.empty_html("No saved advice yet", "Every answer you get is kept here, so you can read it again without asking."),
                    unsafe_allow_html=True)
    for a in farm["advice"]:
        with st.expander(f"{a['title']}  ·  {a['time'].replace('T', ' ')}"):
            if a.get("text"):
                sh.render_result(a["text"])
    with st.expander("Tips for weak internet"):
        st.markdown("- Turn on **Low-data mode** in the sidebar: no web font, no animation, smaller photos and no web-search extras.\n"
                    "- The forecast is saved, so the last one still shows when you are offline.\n"
                    "- Spoken answers use your phone's own voice, so they use no data.\n"
                    "- Photos are shrunk before they are sent.\n"
                    "- Download your offline pack and farm file when you have a good connection.")
