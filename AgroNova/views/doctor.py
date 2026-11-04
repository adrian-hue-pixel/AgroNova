"""Plant Doctor: photo + symptoms -> Novi asks smart follow-up questions -> possible causes.

Flow (kept in st.session_state["doctor"]):  intake -> questions -> result.
The photo is shrunk before it is sent (faster, cheaper, works on weak connections).
Results are POSSIBILITIES, never a confirmed diagnosis.
"""
import streamlit as st

from utils import prompts, store, ui
from utils.gemini import GeminiError, generate_json, has_api_key
from views import shared as sh

PARTS = ["Leaves", "Stem", "Roots", "Fruit / grain", "Flowers", "Whole plant"]
TREATMENT = ["Organic / natural only", "Conventional is fine", "Both - show me options"]


def _state() -> dict:
    return st.session_state.setdefault("doctor", {"stage": "intake"})


def _reset() -> None:
    st.session_state["doctor"] = {"stage": "intake"}
    st.session_state["doc_n"] = st.session_state.get("doc_n", 0) + 1     # new uploader, so the old photo is gone


def _save_to_journal() -> None:
    d = _state()
    thumb = store.make_thumbnail(d["photo"]) if d.get("photo") else ""
    store.add_journal(sh.farm(), {"date": sh.today().isoformat(), "crop": d["crop"], "kind": "Pest or disease",
                                  "note": f"Plant Doctor check. Symptoms: {d['symptoms'][:300]}", "treatment": "",
                                  "weather": "", "qty": "", "qty_unit": "", "cost": "", "photo": thumb})
    d["journaled"] = True


def _intake() -> None:
    p = sh.profile()
    with st.form("doctor_intake"):
        crop = st.text_input("Crop name *", value=p["crops"][0]["name"] if p["crops"] else "", placeholder="e.g. tomato, paddy, cotton")
        parts = st.multiselect("Which parts are affected? *", PARTS)
        symptoms = st.text_area("What do you see?", placeholder="e.g. yellow leaves with brown spots, starting from the bottom", height=90)
        photo = st.file_uploader("Photo of the leaf or crop (optional, but it helps)", type=["jpg", "jpeg", "png", "webp"], key=f"doc_photo_{st.session_state.get('doc_n', 0)}")
        st.caption("Tip: take the photo in daylight, close to the problem, with one leaf filling most of the picture.")
        treat = st.selectbox("Treatment preference", TREATMENT)
        go_next = st.form_submit_button("Next: Novi asks a few questions", type="primary")
    if not go_next:
        return
    problems = []
    if not crop.strip():
        problems.append("Please type the crop name.")
    if not parts:
        problems.append("Please choose at least one affected plant part.")
    if not symptoms.strip() and photo is None:
        problems.append("Please describe what you see or upload a photo.")
    if len(symptoms) > 1000:
        problems.append("The description is too long (maximum 1000 characters).")
    if problems:
        for m in problems:
            st.error(m)
        return
    image = None
    if photo is not None:
        try:
            image = store.prepare_image(photo.getvalue(), max_px=640 if sh.prefs()["low_data"] else 1024)
        except ValueError as e:
            st.error(str(e))
            return
    d = {"stage": "questions", "crop": crop.strip(), "parts": ", ".join(parts), "symptoms": symptoms.strip(),
         "treat": treat, "photo": image[0] if image else None, "mime": image[1] if image else None,
         "questions": [], "journaled": False, "run": store.new_id()}
    prompt = prompts.build_question_prompt(d["crop"], sh.profile()["region"], d["symptoms"], d["parts"],
                                           sh.prefs()["language"], bool(image))
    ph = sh.loader(("Novi is looking closely...", "Thinking of the right questions..."))
    try:
        d["questions"] = prompts.parse_questions(generate_json(prompt, images=[image] if image else None))
    except GeminiError as e:
        ph.empty()
        st.error(str(e))
        return
    ph.empty()
    st.session_state["doctor"] = d
    st.rerun()


def _questions() -> None:
    d = _state()
    if d.get("photo"):
        st.image(d["photo"], width=240, caption="Your photo")
    st.markdown(f"**{d['crop']}** · {d['parts']}")
    if not d["questions"]:
        st.info("Novi has no extra questions. You can get the possible causes now.")
    with st.form("doctor_questions"):
        answers = []
        for i, q in enumerate(d["questions"]):
            with st.container(key=f"qcard_{i}"):
                answers.append(st.radio(f"{i + 1}. {q['question']}", q["options"], index=None, key=f"docq_{d['run']}_{i}"))
        submit = st.form_submit_button("Get possible causes", type="primary")
    st.button("Start over", on_click=_reset, key="doc_restart_q")
    if not submit:
        return
    qa = "; ".join(f"{q['question']} -> {a or 'not answered'}" for q, a in zip(d["questions"], answers))
    ctx = {"Crop": d["crop"], "Country": sh.profile()["country"], "Region": sh.profile()["region"],
           "Affected plant parts": d["parts"], "Symptoms described": d["symptoms"] or "(see photo)",
           "Farmer's answers to follow-up questions": qa, "Treatment preference": d["treat"],
           "Photo provided": "yes" if d.get("photo") else "no"}
    prompt = sh.build_prompt("doctor", ctx, sh.forecast_extra())
    images = [(d["photo"], d["mime"])] if d.get("photo") else None
    text, links = sh.run_ai(prompt, images=images, messages=("Novi is studying the photo...", "Comparing the likely causes...",
                                                               "Writing simple advice for you..."))
    if text:
        d.update({"stage": "result", "answers": qa})
        sh.save_result("doctor", f"Plant Doctor: {d['crop']}", text, links, country=sh.profile()["country"])
        st.rerun()


def _result() -> None:
    d = _state()
    res = st.session_state["results"].get("doctor")
    c1, c2 = st.columns([1, 3])
    if d.get("photo"):
        c1.image(d["photo"], width=200)
    c2.markdown(f"**{d['crop']}** · {d['parts']}")
    c2.caption("These are possible causes from the information and photo you gave. They are not a confirmed diagnosis.")
    if res:
        sh.render_result(res["text"])
        sh.advice_tools("doctor", res["text"], res["time"], res.get("links"), sh.profile()["country"])
    b1, b2 = st.columns(2)
    if d.get("journaled"):
        b1.success("Saved in your farm journal.")
    else:
        b1.button("Save this check in my farm journal", on_click=_save_to_journal, key="doc_journal")
    b2.button("Check another plant", on_click=_reset, type="primary", key="doc_restart_r")


def page_doctor() -> None:
    sh.page_header("doctor", "Plant Doctor", "Upload a photo, answer a few questions, and see what could be wrong.")
    if not has_api_key():
        st.error("The Gemini API key is not configured yet. See the README (API key configuration).")
    sh.needs_profile_hint()
    stage = _state()["stage"]
    steps = {"intake": "Step 1 of 3: Tell Novi what you see", "questions": "Step 2 of 3: A few quick questions",
             "result": "Step 3 of 3: Possible causes"}
    st.markdown(ui.badge_html(steps.get(stage, steps["intake"]), "sky"), unsafe_allow_html=True)
    {"intake": _intake, "questions": _questions, "result": _result}.get(stage, _intake)()
