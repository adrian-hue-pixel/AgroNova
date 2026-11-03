# 🌱 AgroNova – Smart Farming Assistant

A Streamlit web app that gives farmers simple, region-specific farming advice using the Google Gemini API.
Built for the Generative AI **Formative Assessment 2 (FA-2)**, following on from the FA-1 storyboard.

**Live app:** `[ADD YOUR STREAMLIT URL AFTER YOU DEPLOY]`  |  **Repository:** `[ADD YOUR GITHUB URL]`

> **Project status (read this first)**
> | Item | Status |
> |---|---|
> | Code written and syntax-checked | ✅ done |
> | Automated unit tests (helpers, prompts, mocked Gemini logic) | ✅ 24 pass |
> | Smoke test of every page using a *fake* Streamlit | ✅ passes (does not prove the real UI renders) |
> | Run with real Streamlit and real Gemini API | ⬜ **you must do this** |
> | Six validation prompts run, results recorded | ⬜ **you must do this** |
> | Deployed on Streamlit Cloud and tested on devices | ⬜ **you must do this** |
>
> Nothing in this repository claims that deployment, device testing or real API tests have been completed.

## 1. Introduction
AgroNova lets a farmer type their country, region, crop, soil and season and receive clear, formatted advice with reasons and
safety warnings, in their preferred language.

## 2. Problem statement
Small and medium-scale farmers in places such as Tamil Nadu (India), Ghana and Canada face erratic rainfall, pests, poor soil and a lack of
timely local advice, which affects yields and food security (UN SDG 2 and SDG 13). Extension officers cannot answer every question quickly.
A generative AI assistant can give instant first-level guidance, if it is carefully designed to stay region-specific, explain its reasoning and avoid unsafe advice.

## 3. Objectives
- Turn the FA-1 plan into a working, deployed application.
- Integrate Gemini through a reusable, secure API function.
- Format AI output into clear sections with reasoning.
- Validate the model with 6 prompts from different regions and improve prompts/parameters.
- Collect user feedback and deploy on Streamlit Community Cloud.

## 4. Target users
Small/medium-scale farmers (and farm advisers) in India, Ghana and Canada, including users who prefer Hindi, Tamil, French and other languages.

## 5. Five core features
| # | Feature | Inputs | Output |
|---|---|---|---|
| 1 | Crop Recommendation | country, region, soil, pH, month, water, land | suitable crops + reasons |
| 2 | Pest & Disease Management | crop, symptoms, plant parts, region, organic/conventional | possible causes with confidence, checks, prevention, treatment |
| 3 | Weather-Based Advice | location, crop, stage, **source of the weather info**, recent rain, temperature, **user-typed** expected weather | irrigation, harvest, planting, risks. Clearly labelled *not a live forecast* |
| 4 | Soil & Fertilizer Advice | soil, pH, crop, nutrient info | suitability, nutrient needs, fertilizer management (no exact doses) |
| 5 | Sustainable Farming | topics, region, crop, farm size | water, organic, natural pest control, rotation, soil conservation |

Extras: multilingual answers (12 languages), input validation, loading spinner, friendly error handling, star rating + comments, CSV feedback export, downloadable advice, API-key status in the sidebar, and a Validation Lab page with V1/V2 side-by-side comparison.

## 6. Technology stack
Python 3 · Streamlit · Google Gemini via the `google-genai` SDK · Pandas (feedback table only) · GitHub · Streamlit Community Cloud.

**Honest note on the model:** the brief mentions Gemini 1.5 and the `google-generativeai` library. Both are retired/deprecated, so this project uses the
supported `google-genai` SDK (version 1.51.0 or newer, which Gemini 3 models need) and the default model **`gemini-3.8-flash`**
(`DEFAULT_MODEL` in `utils/gemini.py`; Google's model list showed it as a stable model when this was written - re-check at https://ai.google.dev/gemini-api/docs/models).
You can change the model without editing code by adding `GEMINI_MODEL = "..."` to your secrets. Write the model you really used in your report.

**Dependencies** (`requirements.txt`): `streamlit>=1.40.0`, `google-genai>=1.51.0`, `pandas>=2.0.0` (used for the feedback table/CSV export and the Validation Lab comparison table). Both libraries are pure Python and have no conflicting pins, but this has **not** been verified by a real `pip install` in the build environment (no internet there) - run the install command below and tell me if it reports a conflict.

## 7. System architecture
```
Farmer (browser) -> Streamlit UI (app.py)
                      |  validate inputs (utils/helpers.py)
                      v
              build prompt (utils/prompts.py)  -> system instruction + task + farmer context + output format
                      v
              generate_advice() (utils/gemini.py) -> Gemini API (key from Streamlit secrets)
                      v
              parse into 5 sections -> Overview / Actions / Why / Precautions / Extras -> feedback form
```

```
AgroNova/
├── app.py                      # UI, pages, forms, result display, feedback, Validation Lab
├── requirements.txt
├── README.md
├── FA2_Submission_Report.md
├── .gitignore
├── tests/                      # automated tests (see Testing)
├── .streamlit/
│   ├── config.toml             # green theme
│   └── secrets.toml.example    # template - the real secrets.toml is git-ignored
├── utils/
│   ├── gemini.py               # reusable API call + error handling
│   ├── prompts.py              # system instruction, task prompts, output format
│   └── helpers.py              # input validation + response parsing
└── data/README.md
```

## 8. How the application works
1. The farmer picks a feature and fills a form (required fields are marked *).
2. `validate_inputs()` rejects empty/invalid entries (e.g. pH outside 0–14).
3. `build_prompt()` adds all the farmer's details to a feature-specific prompt.
4. `generate_advice()` calls Gemini and returns text or a friendly `GeminiError`.
5. `parse_sections()` splits the answer into five sections that are shown with `st.info`, `st.warning`, `st.expander` etc.
6. The farmer rates the answer; feedback is stored.

## 9. Gemini API integration
`utils/gemini.py` contains one reusable function, `generate_advice(prompt, ...)`. The key is read from `st.secrets["GEMINI_API_KEY"]` (never hard-coded).
Everything is sent in one `GenerateContentConfig`: the **system instruction**, `temperature=0.3` (consistent, factual), and `max_output_tokens=8192`
(on Gemini 3 this limit also counts hidden "thinking" tokens, so it is set generously; answers themselves are ~450 words).
Thinking is set per model family: Gemini 3.x gets `thinking_level=LOW`, Gemini 2.5 Flash gets `thinking_budget=0`; the two are never sent together because Gemini 3 rejects that. If an answer hits the length limit the app tells the user. Handled errors: missing/invalid key, quota (429),
unknown model (404), server errors (5xx), network failure, and empty/blocked responses.

## 10. Prompt engineering approach
- **Role + rules** in a system instruction (simple language, explain why, never invent weather, never state uncertain diagnoses as fact, no exact doses, recommend local experts).
- **Context injection:** every prompt includes location, crop, soil, season, water and preferences.
- **Fixed output format** with five headings so answers are structured and predictable.
- **Language rule:** answers in the chosen language while headings stay English for parsing.

## 11. Output formatting and reasoning
Answers are shown as **Overview → Recommended actions → Why these recommendations → Precautions → Additional suggestions**. If the model ignores the format,
the raw Markdown is displayed as a fallback so the farmer still gets an answer.

## 12. Model validation and optimization
Use the app's **🧪 Validation Lab** page:
1. Pick one of the six test prompts (India ×3, Ghana ×2, Canada ×1) or edit the prompt.
2. Choose **Compare V1 and V2 side by side** (2 API calls), or run one version. **V1** = your question sent as-is. **V2** = engineered prompt + system instruction + output format.
3. The page shows the original prompt, the engineered prompt, both real Gemini responses, simple automatic counts (words, list items, 5-section format, expert referral, uncertainty words, possible exact doses) and text similarity.
4. Adjust the **temperature** slider and re-run to see the effect.
5. Tick the **five-point checklist** for each answer, add notes (which FAO / government source you compared with), and **save to the log**.
6. Download the log as **Markdown** or **JSON** and use it in your report.

Results are only ever produced by real API calls made when you press *Run test*. Nothing is pre-filled. The automatic counts are not a quality score - you judge accuracy yourself.

## 13. Feedback collection
Each result has a 1–5 star rating and comment box. Feedback is kept for the session and appended to `data/feedback.csv` (temporary on Streamlit Cloud;
download it from the About page).

## 14. Installation
```bash
git clone <your-repo-url>     # or unzip AgroNova.zip
cd AgroNova
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 15. API key configuration
1. Open https://aistudio.google.com/app/apikey, sign in, click **Create API key**.
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste your key after `GEMINI_API_KEY =`.
3. Never commit `secrets.toml` (it is in `.gitignore`).

Run: `streamlit run app.py`

## 16. Deployment (Streamlit Community Cloud)
1. Create a **public** GitHub repository (e.g. `AgroNova`), upload all files (do **not** upload `secrets.toml`).
2. Go to https://share.streamlit.io, sign in with GitHub, click **Create app**.
3. Choose your repository, branch `main`, main file `app.py`.
4. Open **Advanced settings → Secrets** and paste: `GEMINI_API_KEY = "your-key"`.
5. Click **Deploy**. When the build finishes you get a public URL like `https://<name>.streamlit.app`.
6. Paste that URL at the top of this README and in your report.

## 17. Testing methodology
**Automated (already run by the developer, see status table):**
```bash
python -m unittest discover -s tests -v                 # 24 tests: helpers, prompts, mocked Gemini logic
python tests/smoke_app_with_stub_streamlit.py            # runs every page against a FAKE Streamlit
```
These tests use fakes: they check our logic, **not** the real Streamlit UI or the real Gemini API.

**Manual (you must do and record):**
1. Run locally (`streamlit run app.py`) and test every page: empty forms, pH = 20, a missing key and a wrong API key (expect friendly errors), each language, feedback submit and CSV download.
2. Run the six Validation Lab prompts (V1 vs V2) and complete the checklist.
3. Test the live URL on at least two devices/browsers (phone + laptop) and keep screenshots.

**Known behaviour:** form fields reset when you leave a page and come back (Streamlit design); generated advice and feedback stay for the session.

## 18. Limitations
- General guidance only; not verified for every district or variety.
- No live weather, soil-test or market data.
- Pests/diseases cannot be confirmed from text; no image diagnosis.
- AI can still make mistakes or translate imperfectly, especially in less-resourced languages.
- Feedback storage on Streamlit Cloud is temporary; free API quota is limited.

## 19. Future improvements
Real weather API, photo-based pest identification, voice input for low-literacy users, a database for feedback, region-specific data from FAO/KVK, offline/SMS access.

## 20. Conclusion
AgroNova shows how prompt engineering, structured output and clear safety rules can turn a general LLM into a usable, responsible farming assistant.
