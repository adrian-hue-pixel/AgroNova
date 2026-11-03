"""SMOKE TEST with a FAKE Streamlit (not the real thing).

Runs app.py top-to-bottom for every page, with and without form submission, using a stub Streamlit and a
fake Gemini SDK. It catches typos, NameErrors, bad dictionary keys and broken code paths.
It does NOT prove the UI renders correctly, and it makes NO real API call.
Run from the project root:  python tests/smoke_app_with_stub_streamlit.py
"""
import os
import runpy
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
from test_gemini_mock import install_fakes  # noqa: E402
from utils.prompts import SECTION_TITLES  # noqa: E402

GOOD = "\n".join(f"## {t}\n- point about {t}" for t in SECTION_TITLES)


def run(page, submit=False, feedback=False, key_present=True):
    _, _, _ = install_fakes()
    st = MagicMock()
    st.secrets = {"GEMINI_API_KEY": "k"} if key_present else {}
    st.cache_resource = lambda *a, **k: (lambda f: f)
    state = {"page": page, "language": "Hindi"}
    if feedback:
        state["feedback"] = [{"time": "t", "feature": "crop", "rating": 5, "language": "Hindi", "comment": "=bad()"}]
    st.session_state = state
    st.columns.side_effect = lambda spec, **k: [st for _ in range(spec if isinstance(spec, int) else len(spec))]
    st.selectbox.side_effect = lambda label, options, **k: options[0]
    st.multiselect.side_effect = lambda label, options, **k: list(options)[:1]
    st.radio.side_effect = lambda label, options, **k: options[0]
    st.slider.side_effect = lambda label, lo, hi, val, *a, **k: val
    st.text_input.return_value = "Tamil Nadu" if submit else ""
    st.text_area.return_value = "yellow leaves" if submit else ""
    st.checkbox.return_value = True
    st.button.return_value = submit
    st.form_submit_button.return_value = submit
    sys.modules["streamlit"] = st
    sys.modules.pop("utils.gemini", None)
    import utils.gemini as g
    g.generate_advice = lambda *a, **k: GOOD
    g.has_api_key = lambda: key_present
    sys.modules.pop("pandas", None) if False else None
    runpy.run_path("app.py", run_name="__main__")
    return st


pages = ["home", "dashboard", "crop", "pest", "weather", "soil", "sustainable", "lab", "about"]
failures = 0
for scenario in ("view", "submit", "no_key"):
    for p in pages:
        try:
            st = run(p, submit=(scenario == "submit"), feedback=(p == "about"), key_present=(scenario != "no_key"))
            print(f"PASS  {scenario:7} {p}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"FAIL  {scenario:7} {p}: {type(e).__name__}: {e}")
print("\nFAILURES:", failures)
# the smoke test submits fake feedback, so delete the CSV it creates
if os.path.exists("data/feedback.csv"):
    os.remove("data/feedback.csv")
sys.exit(1 if failures else 0)
