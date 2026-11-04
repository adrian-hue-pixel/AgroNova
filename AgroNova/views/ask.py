"""Ask by Voice: speak a question (Gemini turns the recording into text), get an answer, and listen to it."""
import hashlib

import streamlit as st

from utils.gemini import GeminiError, transcribe_audio
from views import shared as sh

EXAMPLES = ["When should I sow my paddy this season?", "My tomato leaves are curling. What should I check?",
            "How can I save water on my vegetable plot?"]


def page_ask() -> None:
    sh.page_header("ask", "Ask by Voice", "Press the microphone, speak your question, then listen to the answer.")
    pr = sh.prefs()
    sh.needs_profile_hint()

    if hasattr(st, "audio_input"):
        audio = st.audio_input("Tap to record your question, tap again to stop", key="ask_audio")
        if audio is not None:
            data = audio.getvalue()
            digest = hashlib.md5(data).hexdigest()  # noqa: S324 - only to avoid re-sending the same recording
            if st.session_state.get("ask_audio_done") != digest:
                ph = sh.loader(("Novi is listening...",))
                try:
                    st.session_state["ask_text"] = transcribe_audio(data, "audio/wav", pr["language"])
                    st.session_state["ask_audio_done"] = digest
                except GeminiError as e:
                    st.error(str(e))
                ph.empty()
        st.caption("You can speak in your language or in English. Please check the words below before asking.")
    else:
        st.info("Voice recording needs a newer Streamlit (1.40 or later). You can still type your question below.")

    question = st.text_area("Your question", key="ask_text", height=110, placeholder="Speak above, or type here. " + EXAMPLES[0])
    if st.button("Ask Novi", type="primary", key="ask_go"):
        q = question.strip()
        if not q:
            st.error("Please speak or type a question first.")
        elif len(q) > 1000:
            st.error("The question is too long (maximum 1000 characters).")
        else:
            ctx = {"Farmer's question": q, **sh.farm_context()}
            text, links = sh.run_ai(sh.build_prompt("ask", ctx, sh.forecast_extra()))
            if text:
                sh.save_result("ask", f"Question: {q[:60]}", text, links, country=sh.profile()["country"])

    res = st.session_state["results"].get("ask")
    if res:
        st.divider()
        sh.render_result(res["text"])
        sh.advice_tools("ask", res["text"], res["time"], res.get("links"), sh.profile()["country"])
