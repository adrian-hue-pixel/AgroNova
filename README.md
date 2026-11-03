<p align="center"> <img src="assets/banner.svg" alt="AgroNova - Smart Farming Assistant" width="100%"> </p> <p align="center"> <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"> <img alt="Google Gemini" src="https://img.shields.io/badge/Google%20Gemini-API-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white"> <img alt="Tests" src="https://img.shields.io/badge/unit%20tests-24%20passing-2EA043?style=for-the-badge"> </p> <p align="center"> <b>Simple questions in. Clear, region-specific farming advice out.</b><br> A Streamlit web app that uses the Google Gemini API to guide farmers in India, Ghana, Canada and beyond. </p> <p align="center"> <a href="#features">Features</a> · <a href="#screenshots">Screenshots</a> · <a href="#how-it-works">How it works</a> · <a href="#quick-start">Quick start</a> · <a href="#deployment">Deployment</a> · <a href="#validation-lab">Validation Lab</a> · <a href="#limitations-and-safety">Safety</a> </p> <p align="center"> <b>Live app:</b> <code>[ADD YOUR STREAMLIT URL]</code> &nbsp;|&nbsp; <b>Repository:</b> <code>[ADD YOUR GITHUB URL]</code> </p>
---

## Overview

AgroNova is a student project for the Generative AI **Formative Assessment 2 (FA-2)**, built on the FA-1 storyboard. A farmer enters their country, region, crop, soil and season, and AgroNova returns formatted advice with reasons and safety warnings, written in their preferred language.

**Why it exists.** Small and medium-scale farmers in places such as Tamil Nadu (India), Ghana and Canada deal with erratic rainfall, pests, poor soil and little timely local advice, which affects yields and food security (UN SDG 2 and SDG 13). Extension officers cannot answer every question quickly. AgroNova offers instant first-level guidance that stays region-specific, explains its reasoning and avoids unsafe advice.

**Who it is for.** Small and medium-scale farmers and farm advisers in India, Ghana and Canada, including people who prefer Hindi, Tamil, French or other languages.

## Features

| Feature | You provide | You get |
|---|---|---|
| **Crop Recommendation** | Country, region, soil, pH, month, water, land | Suitable crops with reasons |
| **Pest & Disease Management** | Crop, symptoms, plant parts, region, organic or conventional | Possible causes with confidence, checks, prevention, treatment |
| **Weather-Based Advice** | Location, crop, stage, source of weather information, recent rain, temperature, expected weather (typed by you) | Irrigation, harvest and planting advice. Clearly labelled *not a live forecast* |
| **Soil & Fertilizer Advice** | Soil, pH, crop, nutrient information | Suitability, nutrient needs, fertilizer management (no exact doses) |
| **Sustainable Farming** | Topics, region, crop, farm size | Water, organic, natural pest control, rotation and soil conservation tips |

**Also included**

- Answers in 12 languages
- Input validation with friendly messages
- Structured results: Overview, Recommended actions, Why these recommendations, Precautions, Additional suggestions
- Star rating and comments, with CSV export
- Downloadable advice
- API-key status in the sidebar
- A **Validation Lab** page for V1 and V2 prompt comparison
- Light and dark appearance, with an animated interface and a mascot, Novi

## Screenshots

> Add your own screenshots to `docs/screenshots/` (the FA-2 brief asks for screenshots or recordings of model interaction, input handling and responsive design), then replace the placeholders below.

| View | File to add |
|---|---|
| Home (dark) | `docs/screenshots/home-dark.png` |
| Home (light) | `docs/screenshots/home-light.png` |
| Dashboard | `docs/screenshots/dashboard.png` |
| A feature form with validation message | `docs/screenshots/form-validation.png` |
| Advice result | `docs/screenshots/result.png` |
| Validation Lab (V1 vs V2) | `docs/screenshots/validation-lab.png` |
| Phone view | `docs/screenshots/mobile.png` |

Markdown to use once the images exist: `![Home](docs/screenshots/home-dark.png)`

## How it works

```
Farmer (browser) -> Streamlit UI (app.py)
                      |  validate inputs            (utils/helpers.py)
                      v
              build prompt                          (utils/prompts.py)
              system instruction + task + farmer context + output format
                      v
              generate_advice()                     (utils/gemini.py)
              Gemini API, key read from Streamlit secrets
                      v
              parse into 5 sections -> Overview / Actions / Why / Precautions / Extras
                      v
              feedback form -> data/feedback.csv
```

1. The farmer picks a feature and fills a form. Required fields are marked with `*`.
2. `validate_inputs()` rejects empty or invalid entries, for example a pH outside 0 to 14.
3. `build_prompt()` adds the farmer's details to a feature-specific prompt.
4. `generate_advice()` calls Gemini and returns text or a friendly `GeminiError`.
5. `parse_sections()` splits the answer into five sections. If the model ignores the format, the raw Markdown is shown instead.
6. The farmer rates the answer and the feedback is stored.

### Gemini integration

`utils/gemini.py` holds one reusable function, `generate_advice(prompt, ...)`. The key comes from `st.secrets["GEMINI_API_KEY"]` and is never hard-coded.

- **Model:** the default is set by `DEFAULT_MODEL` in `utils/gemini.py`. You can override it without editing code by adding `GEMINI_MODEL = "..."` to your secrets. Check the current model list at <https://ai.google.dev/gemini-api/docs/models> and record the model you actually used in your report.
- **SDK:** the brief mentions Gemini 1.5 and `google-generativeai`, which are deprecated. This project uses the current `google-genai` SDK (1.51.0 or newer).
- **Settings:** the system instruction, `temperature=0.3` (consistent and factual) and `max_output_tokens=8192` are sent together in one `GenerateContentConfig`. On Gemini 3 the token limit also counts hidden thinking tokens, so it is set generously.
- **Handled errors:** missing or invalid key, quota (429), unknown model (404), server errors (5xx), network failure, and empty or blocked responses.

### Prompt engineering

- **Role and rules** in a system instruction: simple language, always explain why, never invent weather, never state an uncertain diagnosis as fact, no exact doses, recommend local experts.
- **Context injection:** every prompt carries location, crop, soil, season, water and preferences.
- **Fixed output format** with five headings, so answers are structured and predictable.
- **Language rule:** answers are written in the chosen language while headings stay in English for parsing.

## Tech stack

Python · Streamlit · Google Gemini (`google-genai`) · Pandas (feedback table and Validation Lab comparison) · GitHub · Streamlit Community Cloud

`requirements.txt`: `streamlit>=1.40.0`, `google-genai>=1.51.0`, `pandas>=2.0.0`

## Quick start

```bash
git clone <your-repo-url>        # or unzip AgroNova.zip
cd AgroNova
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**API key**

1. Create a key at <https://aistudio.google.com/app/apikey>.
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste your key after `GEMINI_API_KEY =`.
3. Never commit `secrets.toml`. It is already in `.gitignore`.

**Run**

```bash
streamlit run app.py
```

## Deployment

Deploy on **Streamlit Community Cloud**:

1. Create a **public** GitHub repository (for example `AgroNova`) and upload all files, **except** `secrets.toml`.
2. Go to <https://share.streamlit.io>, sign in with GitHub and click **Create app**.
3. Choose your repository, branch `main` and main file `app.py`.
4. Open **Advanced settings, Secrets** and paste `GEMINI_API_KEY = "your-key"`.
5. Click **Deploy**. When the build finishes you get a public URL like `https://<name>.streamlit.app`.
6. Paste the URL at the top of this README and in your report, then test it on at least two devices or browsers.

## Validation Lab

The **Validation Lab** page supports the model-validation step of the brief.

1. Pick one of the six test prompts (India ×3, Ghana ×2, Canada ×1) or edit the prompt.
2. Compare **V1** (your question sent as-is) with **V2** (engineered prompt, system instruction and output format), or run one version.
3. Review the original prompt, the engineered prompt, both real Gemini responses, simple automatic counts and text similarity.
4. Adjust the **temperature** slider and run again to see its effect.
5. Tick the five-point checklist for each answer, note which FAO or government source you compared with, and save it to the log.
6. Download the log as Markdown or JSON for your report.

**Feedback checklist**

- Is the advice specific to the input region?
- Does the output provide valid and logical reasoning?
- Is the language simple enough for a layperson?
- Are the outputs not too generic or technical?
- Does the model avoid misleading or unsafe advice?

Every answer is a real API response produced when you press **Run test**. Nothing is pre-filled, and the automatic counts are not a quality score: you judge accuracy against trusted sources.

## Project structure

```
AgroNova/
├── app.py                      # pages, forms, results, feedback, Validation Lab
├── requirements.txt
├── README.md
├── FA2_Submission_Report.md
├── assets/
│   └── banner.svg              # animated README banner
├── docs/screenshots/           # add your screenshots here
├── tests/                      # unit tests and a page-by-page smoke test
├── .streamlit/
│   ├── config.toml             # base theme
│   └── secrets.toml.example    # template; the real secrets.toml is git-ignored
├── utils/
│   ├── gemini.py               # reusable API call and error handling
│   ├── prompts.py              # system instruction, task prompts, output format
│   ├── helpers.py              # input validation and response parsing
│   └── ui.py                   # design system: themes, animated background, mascot, components
└── data/                       # feedback.csv is written here at runtime
```

## Testing

```bash
python -m unittest discover -s tests -v            # 24 tests: helpers, prompts, mocked Gemini logic
python tests/smoke_app_with_stub_streamlit.py       # runs every page against a fake Streamlit
```

These tests use fakes. They check AgroNova's logic, not the real Gemini API or how the page looks in a browser.

**Manual checks to record for the report**

- Run locally and try every page: empty forms, pH = 20, a missing key, a wrong key, each language, feedback submit and CSV download.
- Run the six Validation Lab prompts (V1 vs V2) and complete the checklist.
- Test the live URL on a phone and a laptop and keep screenshots.

**Project status**

- [x] App, prompts, API wrapper and Validation Lab written
- [x] 24 unit tests and the page smoke test pass
- [ ] Run with the real Gemini API and record results
- [ ] Six validation prompts run and checklist completed
- [ ] Deployed on Streamlit Cloud and tested on multiple devices
- [ ] Screenshots added to `docs/screenshots/`

## Limitations and safety

- Advice is general AI-generated guidance, not verified for every district or crop variety. Always confirm important decisions with a local agricultural officer.
- There is **no live weather data**. Weather advice uses only what the user types in. For real forecasts use a national weather service.
- Pest and disease results are possibilities, not a confirmed diagnosis, and there is no image diagnosis.
- The assistant is instructed never to give exact pesticide or fertilizer doses. Follow product labels and local guidance.
- Translations can be imperfect, especially in less widely used languages.
- Feedback storage on Streamlit Cloud is temporary, and free API quota is limited.
- Form fields reset when you leave a page and return; generated advice and feedback stay for the session.

## Roadmap

- Real weather API integration
- Photo-based pest identification
- Voice input for low-literacy users
- A database for feedback
- Region-specific data from FAO and local agricultural extension services
- Offline or SMS access

## Acknowledgements

Built for the Generative AI **Formative Assessment 2: Designing a Smart Farming Assistance Web App using Generative AI**. Powered by Google Gemini and Streamlit.
