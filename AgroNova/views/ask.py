"""Ask by Voice: speak a question (Gemini turns the recording into text), get an answer, and listen to it."""
import hashlib

import streamlit as st

from utils.gemini import GeminiError, transcribe_audio
from utils import voice
from views import shared as sh

EXAMPLES = ["When should I sow my paddy this season?", "My tomato leaves are curling. What should I check?",
            "How can I save water on my vegetable plot?"]


def page_ask() -> None:
    sh.page_header("ask", "Ask by Voice", "Press the microphone, speak your question, then listen to the answer.")
    pr = sh.prefs()
    sh.needs_profile_hint()
    reply_choice = st.selectbox("Reply language", ["Automatic", *sh.LANGUAGES], key="ask_reply_language",
                               help="Automatic matches Tamil and other supported Indian scripts. For Romanised Tamil, French, Spanish or another language, choose the language here. Otherwise it uses your sidebar language.")
    selected_language = pr["language"] if reply_choice == "Automatic" else reply_choice
    recording = None

    if hasattr(st, "audio_input"):
        audio = st.audio_input("Tap to record your question, tap again to stop", key="ask_audio")
        recording = audio
        if audio is not None:
            data = audio.getvalue()
            digest = hashlib.md5(data + selected_language.encode()).hexdigest()  # noqa: S324 - only to avoid re-sending the same recording
            if st.session_state.get("ask_audio_done") != digest:
                ph = sh.loader(("Novi is listening...",))
                try:
                    st.session_state["ask_text"] = transcribe_audio(data, "audio/wav", selected_language)
                    st.session_state["ask_audio_done"] = digest
                except GeminiError as e:
                    st.error(str(e))
                ph.empty()
        st.caption("You can speak in your language or in English. Please check the words below before asking.")
    else:
        st.info("Voice recording needs a newer Streamlit (1.40 or later). You can still type your question below.")

    uploaded = st.file_uploader("Or upload a voice recording", type=["wav", "mp3", "m4a", "ogg"], key="ask_audio_file")
    if uploaded is not None and recording is None:
        data = uploaded.getvalue()
        digest = hashlib.md5(data + selected_language.encode()).hexdigest()
        if st.session_state.get("ask_audio_done") != digest:
            mime = {"wav": "audio/wav", "mp3": "audio/mpeg", "m4a": "audio/mp4", "ogg": "audio/ogg"}.get(uploaded.name.rsplit(".", 1)[-1].lower(), "audio/wav")
            try:
                with st.spinner("Novi is listening..."):
                    st.session_state["ask_text"] = transcribe_audio(data, mime, selected_language)
                st.session_state["ask_audio_done"] = digest
            except GeminiError as e:
                st.error(str(e))

    question = st.text_area("Your question", key="ask_text", height=110, placeholder="Speak above, or type here. " + EXAMPLES[0])
    if st.button("Ask Novi", type="primary", key="ask_go"):
        q = question.strip()
        if not q:
            st.error("Please speak or type a question first.")
        elif len(q) > 1000:
            st.error("The question is too long (maximum 1000 characters).")
        else:
            ctx = {"Farmer's question": q, **sh.farm_context()}
            reply_language = voice.question_language(q, selected_language) if reply_choice == "Automatic" else selected_language
            text, links = sh.run_ai(sh.build_prompt("ask", ctx, sh.forecast_extra(), language=reply_language))
            if text:
                sh.save_result("ask", f"Question: {q[:60]}", text, links, country=sh.profile()["country"], language=reply_language)

    res = st.session_state["results"].get("ask")
    if res:
        st.divider()
        st.caption(f"Answer language: {res.get('language', pr['language'])}")
        sh.render_result(res["text"])
        sh.advice_tools("ask", res["text"], res["time"], res.get("links"), sh.profile()["country"], language=res.get("language", pr["language"]))
