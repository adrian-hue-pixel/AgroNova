"""Validation Lab (V1 basic prompt vs V2 engineered prompt) and the About & Safety page."""
import datetime
import json

import pandas as pd
import streamlit as st

from utils import ui
from utils.gemini import DEFAULT_TEMPERATURE, GeminiError, active_model, generate_advice, has_api_key
from utils.helpers import compare_outputs, output_metrics, safe_csv_cell, validation_log_markdown
from utils.prompts import SYSTEM_INSTRUCTION, build_free_prompt

TEST_CASES = {
    "TEST 1 - India (Tamil Nadu)": "What crops can I grow in Tamil Nadu during the monsoon season with moderate water availability?",
    "TEST 2 - Ghana": "What sustainable methods can I use to manage pests in my maize farm in Ghana?",
    "TEST 3 - Canada": "What precautions should I take when growing vegetables in a region with a short growing season in Canada?",
    "TEST 4 - India (tomato)": "My tomato plants have yellowing leaves. What could be the possible causes and what should I check?",
    "TEST 5 - Ghana (sandy soil)": "What soil management methods can improve crop growth in sandy soil in Ghana?",
    "TEST 6 - India (Rajasthan)": "What are some water conservation methods for small-scale farmers in Rajasthan?",
}
CHECKLIST = [
    "Is the advice specific to the input region?",
    "Does the output provide valid and logical reasoning?",
    "Is the language simple enough for a layperson?",
    "Are the outputs NOT too generic or technical?",
    "Does the model avoid misleading or unsafe advice?",
]



def run_lab_test(question: str, temperature: float, mode: str, language: str) -> dict:
    """Make the real Gemini call(s) for one Validation Lab run. Nothing is simulated."""
    versions = ["V1", "V2"] if mode.startswith("Compare") else ["V1"] if mode.startswith("V1") else ["V2"]
    results = []
    for v in versions:
        engineered = v == "V2"
        prompt = build_free_prompt(question, language, engineered)
        with st.spinner(f"Calling Gemini for {v}..."):
            try:
                answer = generate_advice(prompt, temperature=temperature,
                                         system_instruction=SYSTEM_INSTRUCTION if engineered else None)
                results.append({"version": v, "prompt_sent": prompt, "system_used": engineered, "answer": answer, "error": None})
            except GeminiError as e:
                results.append({"version": v, "prompt_sent": prompt, "system_used": engineered, "answer": None, "error": str(e)})
    st.session_state["lab_run_id"] += 1
    return {"run_id": st.session_state["lab_run_id"], "question": question, "temperature": temperature,
            "model": active_model(), "language": language, "results": results,
            "time": datetime.datetime.now().isoformat(timespec="seconds")}


def page_lab():
    st.markdown(ui.page_header("lab", "", "Validation Lab", "Compare a basic prompt (V1) with the engineered prompt (V2), "
                               "tick the checklist and download your results."), unsafe_allow_html=True)
    st.info("Every answer shown here is a real response from the Gemini API, produced when you press **Run test**. "
            "Nothing is pre-filled. You must compare the answers with trusted sources (FAO, government farming portals) yourself.")
    if not has_api_key():
        st.error("The Gemini API key is not configured, so tests cannot run. See the README (API key configuration).")

    name = st.selectbox("Test case", list(TEST_CASES))
    question = st.text_area("Original prompt (you can edit it)", TEST_CASES[name], key=f"lab_q_{name}")
    c1, c2 = st.columns(2)
    mode = c1.radio("What to run", ["Compare V1 and V2 side by side (2 API calls)", "V1 only - basic prompt", "V2 only - engineered prompt"])
    temp = c2.slider("Temperature", 0.0, 1.0, DEFAULT_TEMPERATURE, 0.1, help="Lower = more consistent and factual. Higher = more varied.")
    language = st.session_state.get("language", "English")
    c2.caption(f"Answer language: {language} (change it in the sidebar)")

    if st.button("▶Run test", type="primary"):
        if not question.strip():
            st.error("Please enter a prompt.")
        elif len(question) > 1000:
            st.error("The prompt is too long (maximum 1000 characters).")
        else:
            st.session_state["lab_current"] = dict(run_lab_test(question.strip(), temp, mode, language), test=name)

    cur = st.session_state.get("lab_current")
    if cur:
        render_lab_run(cur)

    log = st.session_state["validation_log"]
    st.divider()
    st.subheader(f"Validation log ({len(log)} saved entries)")
    if log:
        d1, d2, d3 = st.columns(3)
        d1.download_button("⬇Markdown", validation_log_markdown(log), file_name="validation_log.md")
        d2.download_button("⬇JSON", json.dumps(log, indent=2, ensure_ascii=False), file_name="validation_log.json")
        if d3.button("Clear log"):
            st.session_state["validation_log"] = []
            st.rerun()
    else:
        st.caption("Nothing saved yet. Run a test, complete the checklist and press 'Save to validation log'.")


def render_lab_run(cur: dict):
    st.divider()
    st.caption(f"{cur['test']} | model {cur['model']} | temperature {cur['temperature']} | language {cur['language']} | {cur['time']}")
    st.markdown("**Original prompt**")
    st.code(cur["question"], language=None)
    results = cur["results"]
    v2 = next((r for r in results if r["version"] == "V2"), None)
    if v2:
        with st.expander("Engineered prompt sent for V2 (plus the system instruction)"):
            st.code(v2["prompt_sent"], language=None)
            st.caption("System instruction sent with V2 only:")
            st.code(SYSTEM_INSTRUCTION, language=None)
    if any(r["version"] == "V1" for r in results):
        st.caption("V1 is sent exactly as typed, with no system instruction and no output format.")

    cols = st.columns(len(results))
    for col, r in zip(cols, results):
        with col:
            st.markdown(f"### {r['version']} response")
            if r["error"]:
                st.error(f"{r['error']}")
            else:
                with st.container(border=True):
                    st.markdown(r["answer"])

    ok = [r for r in results if r["answer"]]
    if len(ok) == 2:
        cmp = compare_outputs(ok[0]["answer"], ok[1]["answer"])
        st.subheader("What changed between V1 and V2?")
        st.dataframe(pd.DataFrame(cmp["metrics"]).astype(str))
        st.write(f"Text similarity between the two answers: **{cmp['similarity']}%**")
        for line in cmp["changes"]:
            st.markdown(f"- {line}")
        st.caption("These are simple automatic counts, not a quality score. Accuracy must be judged by you against trusted sources.")

    if ok:
        st.subheader("Feedback checklist")
        ticks = {}
        cols = st.columns(len(ok))
        for col, r in zip(cols, ok):
            with col:
                st.markdown(f"**{r['version']}**")
                ticks[r["version"]] = {item: st.checkbox(item, key=f"chk_{cur['run_id']}_{r['version']}_{i}")
                                       for i, item in enumerate(CHECKLIST)}
        notes = st.text_area("Problems found, prompt/parameter changes, and validation comments "
                             "(which source did you compare with?)", key=f"lab_notes_{cur['run_id']}")
        if st.button("Save to validation log"):
            similarity = compare_outputs(ok[0]["answer"], ok[1]["answer"])["similarity"] if len(ok) == 2 else None
            for r in ok:
                st.session_state["validation_log"].append({
                    "saved_at": datetime.datetime.now().isoformat(timespec="seconds"), "run_id": cur["run_id"],
                    "test": cur["test"], "version": r["version"], "model": cur["model"], "temperature": cur["temperature"],
                    "language": cur["language"], "original_prompt": cur["question"], "prompt_sent": r["prompt_sent"],
                    "system_instruction_used": r["system_used"], "answer": r["answer"], "metrics": output_metrics(r["answer"]),
                    "v1_v2_similarity_percent": similarity, "checklist": ticks[r["version"]], "notes": notes})
            st.success(f"Saved {len(ok)} entr{'y' if len(ok) == 1 else 'ies'}. The log now has {len(st.session_state['validation_log'])}.")


def page_about():
    st.markdown(ui.page_header("about", "", "About & Safety", "What AgroNova can and cannot do."), unsafe_allow_html=True)
    st.markdown(f"""
**AgroNova** is a student project for the Generative AI assessment. It uses the Google Gemini API
(current model setting: `{active_model()}`).

**Important limits**
- Answers are **general guidance generated by AI**, not verified local recommendations.
- The **forecast** comes from Open-Meteo. Simple rules turn it into watering and spraying hints; they are not agronomic prescriptions.
- **Photo and question-based results are possibilities, not a confirmed diagnosis.** A photo cannot show everything.
- **Prices** are shown only when an official source or the farmer provides them. AgroNova never invents a price.
- **Advice sources** are official portals chosen by country and topic. They help you check the advice; they do not prove each sentence.
- It is instructed never to give exact pesticide or fertilizer doses. Follow product labels and ask your local agricultural officer.
- AI can make mistakes, and translations into some languages may be imperfect. Spoken answers depend on the voices on your device.

**Your data**
- Your farm data stays in your browser session unless you download your farm file (or the app owner turns on local saving).
- Photos are shrunk and sent to Google's Gemini API only when you ask for advice about them.

**Data credits**
- Weather: Open-Meteo.com (CC BY 4.0). Mandi prices (India, optional): Government of India open data, data.gov.in.
""")
    st.subheader("Feedback received this session")
    if st.session_state["feedback"]:
        df = pd.DataFrame(st.session_state["feedback"])
        st.dataframe(df)
        export = df.copy()
        for col in export.columns:
            export[col] = export[col].map(safe_csv_cell)
        st.download_button("⬇Download feedback (CSV)", export.to_csv(index=False), file_name="agronova_feedback.csv")
    else:
        st.caption("No feedback yet. Submit a rating after getting advice and it will appear here.")


