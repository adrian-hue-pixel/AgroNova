"""AgroNova - Smart Farming Assistant (Streamlit + Google Gemini).

Run locally:  streamlit run app.py
"""
import csv
import datetime
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.gemini import DEFAULT_TEMPERATURE, GeminiError, active_model, generate_advice, has_api_key
from utils.helpers import compare_outputs, output_metrics, parse_sections, safe_csv_cell, validation_log_markdown, validate_inputs
from utils.prompts import SYSTEM_INSTRUCTION, build_free_prompt, build_prompt
from utils import ui

st.set_page_config(page_title="AgroNova - Smart Farming Assistant", page_icon="🌿", layout="wide")

FEEDBACK_FILE = Path(__file__).parent / "data" / "feedback.csv"

COUNTRIES = ["India", "Ghana", "Canada", "Kenya", "Brazil", "Italy", "Other"]
LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam", "Marathi", "Bengali",
             "French", "Spanish", "Portuguese", "Twi (Ghana)"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]
SOILS = ["Not sure", "Sandy", "Loamy", "Clay", "Silty", "Red / laterite", "Black (cotton) soil", "Peaty / organic"]
NO_WEATHER_INFO = "I do not know the weather"
WEATHER_SOURCES = ["I checked a weather app or forecast", "A radio broadcast or extension officer told me",
                   "I observed it myself (sky, wind, rain)", NO_WEATHER_INFO]
WATER = ["Very low (rain only, frequent dry spells)", "Moderate", "Good (irrigation available)"]

# ---------------------------------------------------------------- feature definitions
# Each feature = a form. Adding or changing a field only needs a change here.
COUNTRY = {"id": "country", "label": "Country", "type": "select", "options": COUNTRIES, "required": True}
REGION = {"id": "region", "label": "State / region / district", "type": "text", "required": True,
          "placeholder": "e.g. Tamil Nadu, Ashanti Region, Ontario"}

FEATURES = {
    "crop": {
        "title": "Crop Recommendation", "icon": "",
        "tagline": "Find out which crops suit your land, season and water.",
        "fields": [
            COUNTRY, REGION,
            {"id": "soil", "label": "Soil type", "type": "select", "options": SOILS, "required": True},
            {"id": "ph", "label": "Soil pH (optional)", "type": "ph", "placeholder": "e.g. 6.5"},
            {"id": "month", "label": "Month or planting season", "type": "select", "options": MONTHS, "required": True},
            {"id": "water", "label": "Water availability", "type": "select", "options": WATER, "required": True},
            {"id": "land", "label": "Land conditions (optional)", "type": "textarea",
             "placeholder": "e.g. small 1-acre plot, slightly sloped, close to a river"},
        ],
    },
    "pest": {
        "title": "Pest & Disease Management", "icon": "",
        "tagline": "Describe what you see on your plants and get possible causes and safe options.",
        "fields": [
            {"id": "crop", "label": "Crop name", "type": "text", "required": True, "placeholder": "e.g. tomato, maize, cotton"},
            COUNTRY, REGION,
            {"id": "symptoms", "label": "Symptoms you can see", "type": "textarea", "required": True,
             "placeholder": "e.g. leaves turning yellow from the bottom, small brown spots, holes in leaves"},
            {"id": "parts", "label": "Affected plant parts", "type": "multiselect",
             "options": ["Leaves", "Stem", "Roots", "Fruit / grain", "Flowers", "Whole plant"], "required": True},
            {"id": "treatment", "label": "Treatment preference", "type": "select",
             "options": ["Organic / natural only", "Conventional is fine", "Both - show me options"], "required": True},
        ],
    },
    "weather": {
        "title": "Weather-Based Advice", "icon": "",
        "tagline": "Tell us the weather you are seeing and get irrigation, harvest and planting advice.",
        "fields": [
            COUNTRY, REGION,
            {"id": "crop", "label": "Crop", "type": "text", "required": True, "placeholder": "e.g. rice, tomato"},
            {"id": "stage", "label": "Crop stage", "type": "select", "required": True,
             "options": ["Not planted yet", "Seedling", "Growing", "Flowering / fruiting", "Ready to harvest"]},
            {"id": "source", "label": "Where does your weather information come from?", "type": "select", "required": True,
             "options": WEATHER_SOURCES},
            {"id": "rain", "label": "Rain in the last 7 days", "type": "select",
             "options": ["No rain", "Light rain", "Moderate rain", "Heavy rain / flooding"]},
            {"id": "temp", "label": "Temperature you are seeing (optional)", "type": "text",
             "placeholder": "e.g. around 35 C in the afternoon"},
            {"id": "weather", "label": "Weather you expect in the next few days", "type": "textarea",
             "required": True, "required_unless": ("source", NO_WEATHER_INFO),
             "placeholder": "e.g. forecast app says rain on Saturday; hot and dry until then"},
        ],
    },
    "soil": {
        "title": "Soil & Fertilizer Advice", "icon": "",
        "tagline": "Check if your soil suits your crop and how to improve it.",
        "fields": [
            COUNTRY, REGION,
            {"id": "crop", "label": "Crop", "type": "text", "required": True, "placeholder": "e.g. groundnut, wheat"},
            {"id": "soil", "label": "Soil type", "type": "select", "options": SOILS, "required": True},
            {"id": "ph", "label": "Soil pH (optional)", "type": "ph", "placeholder": "e.g. 5.5"},
            {"id": "nutrients", "label": "Soil test / nutrient information (optional)", "type": "textarea",
             "placeholder": "e.g. low nitrogen, medium phosphorus (from a soil health card)"},
        ],
    },
    "sustainable": {
        "title": "Sustainable Farming", "icon": "",
        "tagline": "Practical, low-cost ways to save water, protect soil and reduce chemicals.",
        "fields": [
            COUNTRY, REGION,
            {"id": "topics", "label": "Topics you want tips on", "type": "multiselect", "required": True,
             "options": ["Water conservation", "Organic farming", "Natural pest management", "Crop rotation",
                         "Soil conservation", "General sustainable practices"]},
            {"id": "crop", "label": "Main crop(s) (optional)", "type": "text", "placeholder": "e.g. millet, vegetables"},
            {"id": "size", "label": "Farm size", "type": "select", "options": ["Small (under 2 acres)", "Medium", "Large"]},
        ],
    },
}

PAGES = ["home", "dashboard", *FEATURES.keys(), "lab", "about"]
PAGE_LABELS = {"home": "Home", "dashboard": "Dashboard", "lab": "Validation Lab", "about": "About & Safety",
               **{k: v["title"] for k, v in FEATURES.items()}}

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

# ---------------------------------------------------------------- styling
st.session_state.setdefault("dark_mode", True)
st.markdown(ui.global_css(bool(st.session_state["dark_mode"])) + ui.background_fx(), unsafe_allow_html=True)

# ---------------------------------------------------------------- session state
st.session_state.setdefault("page", "home")
st.session_state.setdefault("results", {})          # feature -> {"text", "time"}
st.session_state.setdefault("feedback", [])         # list of feedback dicts
st.session_state.setdefault("validation_log", [])   # list of Validation Lab entries
st.session_state.setdefault("question_count", 0)
st.session_state.setdefault("lab_run_id", 0)


def go(page: str):
    """Button callback: change the page (runs before the next rerun, so it is safe to set the widget key)."""
    st.session_state["page"] = page


# ---------------------------------------------------------------- helpers
def render_field(prefix: str, f: dict):
    key = f"{prefix}_{f['id']}"
    label = f["label"] + (" *" if f.get("required") else "")
    kind = f["type"]
    if kind in ("text", "ph"):
        return st.text_input(label, key=key, placeholder=f.get("placeholder", ""))
    if kind == "textarea":
        return st.text_area(label, key=key, placeholder=f.get("placeholder", ""), height=100)
    if kind == "select":
        return st.selectbox(label, f["options"], key=key)
    if kind == "multiselect":
        return st.multiselect(label, f["options"], key=key)


def render_result(text: str):
    """Show Gemini's answer as clear, animated section cards instead of one long paragraph."""
    sections = parse_sections(text)
    if not sections:  # the model ignored the format: still show the answer, nicely
        st.markdown(text)
        return
    layout = [("sec_0", "", "Overview", "Overview"), ("sec_1", "", "Recommended actions", "Recommended Actions"),
              ("sec_2", "", "Why these recommendations?", "Why These Recommendations"),
              ("sec_3", "", "Precautions", "Precautions")]
    for box, icon, title, name in layout:
        with st.container(key=box):
            st.markdown(ui.section_title(icon, title), unsafe_allow_html=True)
            st.markdown(sections[name])
    with st.container(key="sec_4"):
        st.markdown(ui.section_title("", "More ideas and follow-up questions"), unsafe_allow_html=True)
        st.markdown(sections["Additional Suggestions"])
    st.success("Remember: this is general guidance. Please confirm important decisions with your local agricultural officer.")


def save_feedback(entry: dict):
    st.session_state["feedback"].append(entry)
    try:
        new_file = not FEEDBACK_FILE.exists()
        with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(entry.keys()))
            if new_file:
                writer.writeheader()
            writer.writerow({k: safe_csv_cell(v) for k, v in entry.items()})
    except OSError:
        pass  # storage can be read-only; the in-session copy is still kept


def feedback_form(feature_key: str):
    st.divider()
    st.subheader("Was this helpful?")
    done_key = f"fbdone_{feature_key}_{st.session_state['results'][feature_key]['time']}"
    if st.session_state.get(done_key):
        st.success("Thank you! Your feedback helps us improve AgroNova.")
        return
    with st.form(f"feedback_{feature_key}"):
        rating = st.radio("Your rating", [1, 2, 3, 4, 5], index=3, horizontal=True, format_func=lambda n: "\u2605" * n)
        comment = st.text_area("Suggestions or problems (optional)", max_chars=500)
        if st.form_submit_button("Submit feedback"):
            save_feedback({"time": datetime.datetime.now().isoformat(timespec="seconds"), "feature": feature_key,
                           "rating": rating, "language": st.session_state.get("language", "English"),
                           "comment": comment.strip()})
            st.session_state[done_key] = True
            st.rerun()


# ---------------------------------------------------------------- pages
def weather_banner():
    st.warning("**This is NOT a live forecast.** AgroNova has no connection to any weather service. "
               "It only uses the weather information **you type in** below.")
    c1, c2 = st.columns(2)
    c1.markdown("**What you provide**  \nRain you saw, temperature, and any forecast you got from a weather app, "
                "radio or officer.")
    c2.markdown("**What AgroNova does**  \nTurns your information into irrigation, harvest and planting advice. "
                "It never adds its own forecast.")
    st.caption("For real forecasts use your national weather service, e.g. IMD (mausam.imd.gov.in) in India, "
               "Ghana Meteorological Agency (meteo.gov.gh), Environment Canada (weather.gc.ca).")


def greeting() -> str:
    hour = datetime.datetime.now().hour
    return "Good morning, farmer" if hour < 12 else "Good afternoon, farmer" if hour < 18 else "Good evening, farmer"


def feature_card(key: str, prefix: str):
    f = FEATURES[key]
    with st.container(key=f"fcard_{prefix}{key}"):
        st.markdown(ui.feature_card_html(key, f["title"], f["tagline"]), unsafe_allow_html=True)
        st.button("Open  \u203a", key=f"open_{prefix}{key}", on_click=go, args=(key,))


def bento(prefix: str):
    """Asymmetric Apple-style grid of feature cards."""
    for keys, widths in ((["crop", "pest"], [1.7, 1]), (["weather", "soil", "sustainable"], [1, 1, 1])):
        for col, key in zip(st.columns(widths, gap="medium"), keys):
            with col:
                feature_card(key, prefix)


def page_home():
    st.markdown(ui.hero_html(len(LANGUAGES), greeting()), unsafe_allow_html=True)
    _, c1, c2, _ = st.columns([2, 1, 1, 2])
    c1.button("Get started", on_click=go, args=("dashboard",), type="primary", key="cta_dash")
    c2.button("Validation Lab", on_click=go, args=("lab",), key="cta_lab")
    st.markdown(ui.steps_html(), unsafe_allow_html=True)
    st.markdown(ui.heading("Everything your farm needs"), unsafe_allow_html=True)
    bento("h_")


def page_dashboard():
    st.markdown(ui.page_header("dashboard", "", "Dashboard", f"{greeting()}. Choose what you need help with today.",
                               "Pick a card to get started."), unsafe_allow_html=True)
    ratings = [fb["rating"] for fb in st.session_state["feedback"]]
    avg = f"{sum(ratings) / len(ratings):.1f} / 5" if ratings else "-"
    s1, s2, s3 = st.columns(3, gap="medium")
    s1.markdown(ui.stat_html(st.session_state["question_count"], "Questions this session", "", .1), unsafe_allow_html=True)
    s2.markdown(ui.stat_html(len(ratings), "Feedback received", "", .2), unsafe_allow_html=True)
    s3.markdown(ui.stat_html(avg, "Average rating", "", .3), unsafe_allow_html=True)
    st.markdown(ui.heading("Your tools"), unsafe_allow_html=True)
    bento("")


def page_feature(key: str):
    f = FEATURES[key]
    st.markdown(ui.page_header(key, f["icon"], f["title"], f["tagline"]), unsafe_allow_html=True)
    if key == "weather":
        weather_banner()
    if not has_api_key():
        st.error("The Gemini API key is not configured yet. See the README (API key configuration).")

    left, right = st.columns([1.8, 1], gap="large")
    with right:
        with st.container(key="aside"):
            st.markdown(ui.aside_html(st.session_state.get("language", "English")), unsafe_allow_html=True)
    with left:
        with st.form(f"form_{key}"):
            values = {fld["id"]: render_field(key, fld) for fld in f["fields"]}
            submitted = st.form_submit_button("Get advice", type="primary")

    if submitted:
        problems = validate_inputs(f["fields"], values)
        if problems:
            for p in problems:
                st.error(p)
        else:
            context = {fld["label"].replace(" (optional)", ""): (", ".join(values[fld["id"]])
                       if isinstance(values[fld["id"]], list) else str(values[fld["id"]]).strip())
                       for fld in f["fields"]}
            prompt = build_prompt(key, context, st.session_state.get("language", "English"))
            loading = st.empty()
            loading.markdown(ui.loader_html(("Novi is thinking about your farm...", "Checking farming knowledge...",
                                             "Writing simple advice for you...")), unsafe_allow_html=True)
            try:
                text = generate_advice(prompt)
            except GeminiError as e:
                loading.empty()
                st.error(f"{e}")
            else:
                loading.empty()
                st.session_state["results"][key] = {"text": text, "time": datetime.datetime.now().isoformat(),
                                                    "source": values.get("source", "")}
                st.session_state["question_count"] += 1

    if key in st.session_state["results"]:
        st.divider()
        text = st.session_state["results"][key]["text"]
        if key == "weather":
            st.info(f"**Based on user-provided weather information** (source you stated: "
                    f"{st.session_state['results'][key].get('source') or 'not stated'}). Not a live forecast.")
        render_result(text)
        st.download_button("⬇Download this advice", text, file_name=f"agronova_{key}.md")
        feedback_form(key)


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
**AgroNova** is a student project for the FA-2 Generative AI assessment. It uses the Google Gemini API
(current model setting: `{active_model()}`).

**Important limits**
- Answers are **general guidance generated by AI**, not verified local recommendations.
- AgroNova has **no live weather data**; weather advice uses only what you type.
- Pest and disease results are **possibilities, not a confirmed diagnosis**.
- It is instructed never to give exact pesticide or fertilizer doses - follow product labels and ask your local agricultural officer.
- AI can make mistakes, and translations into some languages may be imperfect. Always double-check important decisions.
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


# ---------------------------------------------------------------- sidebar + routing
with st.sidebar:
    st.markdown(ui.sidebar_brand(), unsafe_allow_html=True)
    st.toggle("Dark appearance", key="dark_mode")
    st.selectbox("Language of the answers", LANGUAGES, key="language")
    if st.session_state["language"] != "English":
        st.caption("AI translations can contain mistakes, especially for less common languages. Please double-check.")
    st.radio("Menu", PAGES, key="page", format_func=PAGE_LABELS.get)
    if has_api_key():
        st.success(f"API key found\nModel: {active_model()}")
    else:
        st.error("API key missing. See README.")
    st.caption("AI advice is general guidance. Confirm with local experts.")

page = st.session_state["page"]
if page == "home":
    page_home()
elif page == "dashboard":
    page_dashboard()
elif page in FEATURES:
    page_feature(page)
elif page == "lab":
    page_lab()
else:
    page_about()
