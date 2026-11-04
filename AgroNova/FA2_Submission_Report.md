# FA-2 Submission Report – AgroNova Smart Farming Assistant

**Student name:** [INSERT]  **Course:** Generative A.I (Artificial Intelligence CRS)  **Assessment:** Formative Assessment 2 (20 marks)
**GitHub repository:** [ADD URL - only after you create it]  **Live Streamlit app:** [ADD URL - only after you deploy it]

> ✏️ Items in **[BRACKETS]** must be completed by you with genuine screenshots, URLs, Gemini outputs and test results. Nothing in this report has been pre-filled with invented results, and it does **not** claim that deployment or device testing has happened. Delete this note before submitting.

**Verification status at the time this report template was prepared**
| Item | Status |
|---|---|
| Code written, syntax checked | Done |
| 24 automated unit tests (pure logic + mocked Gemini wrapper) | Passed |
| Smoke test of all pages with a fake Streamlit | Passed (does not prove the real UI works) |
| Real `pip install`, real Streamlit run, real Gemini call | **Not done by the developer: [YOU: record the date you did this and the outcome]** |
| Deployment on Streamlit Cloud, multi-device testing | **[YOU: complete]** |

## A. Introduction and project objective
FA-1 planned a Smart Farming Assistant for the fictional company AgroNova. The objective of FA-2 is to turn that plan into a working web application that
(1) gets useful, formatted farming advice from Google Gemini, (2) is validated and optimised using diverse test prompts, and (3) is deployed on Streamlit Cloud
so that pilot farmers in Canada, India and Ghana can use it and give feedback.

## B. The Smart Farming Assistant
AgroNova is a browser-based assistant. A farmer chooses a feature, enters details such as country, region, crop, soil, season and water availability,
and receives structured advice with reasons and safety warnings in one of 12 languages. Link to FA-1: [briefly mention your FA-1 persona and the 5 challenges from your storyboard].

## C. The five compulsory features
1. **Crop Recommendation** – suitable crops for region, soil, pH, month, water and land.
2. **Pest & Disease Management** – possible causes with confidence level, checks, prevention and organic/conventional options; never a confirmed diagnosis.
3. **Weather-Based Advice** – uses only weather typed by the farmer (no live weather API). The page shows a "not a live forecast" warning, asks where the farmer's weather information came from (app, radio/officer, own observation, or unknown), recent rain and temperature, and the result is labelled "Based on user-provided weather information". The model is instructed to add no forecast of its own.
4. **Soil & Fertilizer Advice** – soil suitability and nutrient management without exact doses.
5. **Sustainable Farming** – water conservation, organic farming, natural pest control, crop rotation, soil conservation.

Screenshots: [INSERT screenshot of each feature page]

## D. Gemini API integration and configuration
- SDK: `google-genai` version 1.51.0 or newer (the `google-generativeai` package named in the brief is deprecated, and Gemini 3 features need ≥1.51.0).
- Model: default `gemini-3.5-flash-lite`, replacing Gemini 1.5 which is no longer available. The model can be changed with the `GEMINI_MODEL` secret. Successfully tested in the local Validation Lab on 2026-11-04.
- API key: stored in Streamlit secrets (`GEMINI_API_KEY`), never in the code or GitHub (`secrets.toml` is in `.gitignore`); the sidebar shows whether a key is found.
- One reusable function, `generate_advice()` in `utils/gemini.py`, sends a single `GenerateContentConfig` containing the **system instruction**, **temperature 0.3** (factual, consistent) and **max_output_tokens 8192** (on Gemini 3 this limit includes hidden thinking tokens, so it is set well above the ~450-word answers).
- Thinking setting: `thinking_level=LOW` for Gemini 3 models, `thinking_budget=0` for Gemini 2.5 Flash; never both.
- Error handling: missing/placeholder key, invalid key, quota/rate limit (429), unknown model (404), server errors (5xx), network failure, empty/blocked answer, and answers cut off by the length limit.
- **[YOU: add what you observed when changing temperature, e.g. in the Validation Lab at 0.0 / 0.3 / 1.0.]**

## E. Output formatting and reasoning
The prompt forces five headings (Overview, Recommended Actions, Why These Recommendations, Precautions, Additional Suggestions). `parse_sections()` splits the
answer and Streamlit components display it: `st.info` for the overview, numbered actions, reasoning bullets, `st.warning` for precautions, `st.expander` for extras, and
`st.success` for the expert-consultation reminder.

Example of formatting (Rajasthan, August – *illustrative format only, not a real test result*):
> **Pearl millet** – Drought-tolerant and grows well in sandy, dry soil.

Your real before/after example: [INSERT raw Gemini text vs. formatted screenshot]

## F. Model validation and optimization
**Method:** The app's *Validation Lab* sends each test prompt to Gemini as **V1** (question only, no system instruction) and **V2** (system instruction + farmer context + required output format), side by side, at a chosen temperature. It shows the original prompt, the engineered prompt, both real responses, simple automatic counts and text similarity. Each answer is then scored with the five-point checklist and compared by you with trusted sources (FAO, ICAR/KVK, Ghana MoFA, Agriculture and Agri-Food Canada). The log is downloaded as Markdown/JSON and summarised below.
**Only record a test as "executed" if you really ran it.**

| Test | Region | Input prompt | Status |
|---|---|---|---|
| 1 | India | What crops can I grow in Tamil Nadu during the monsoon season with moderate water availability? | [Executed on DATE / Not yet executed] |
| 2 | Ghana | What sustainable methods can I use to manage pests in my maize farm in Ghana? | [ ] |
| 3 | Canada | What precautions should I take when growing vegetables in a region with a short growing season in Canada? | [ ] |
| 4 | India | My tomato plants have yellowing leaves. What could be the possible causes and what should I check? | [ ] |
| 5 | Ghana | What soil management methods can improve crop growth in sandy soil in Ghana? | [ ] |
| 6 | India | What are some water conservation methods for small-scale farmers in Rajasthan? | [ ] |

Copy this block once for **each** test:

### Test N – [Region]
- **Model / temperature / date:** [from your validation log]
- **Initial AI response (V1):** [PASTE genuine output or a summary of it]
- **Problems identified:** [e.g. generic, too technical, no region detail, missing warnings, too long, exact doses]
- **Prompt / parameter changes:** [e.g. system instruction added, farmer context added, five-section format, temperature changed from __ to __]
- **Improved response (V2):** [PASTE genuine output or a summary of it]
- **What changed (from the comparison table):** [words, list items, 5-section format, expert referral, similarity %]
- **Validation comments:** [Was it accurate? Which source did you compare with? Any hallucination or bias?]

**Overall summary of optimisation:** [3–5 sentences in your own words, based on your real results]

## G. Feedback checklist
| Question | T1 | T2 | T3 | T4 | T5 | T6 |
|---|---|---|---|---|---|---|
| Is the advice specific to the input region? | | | | | | |
| Does the output provide valid and logical reasoning? | | | | | | |
| Is the language simple enough for a layperson? | | | | | | |
| Are the outputs NOT too generic or technical? | | | | | | |
| Does the model avoid misleading or unsafe advice? | | | | | | |

(Fill with ✔ / ✘ from your own Validation Lab log, one table for V1 and one for V2 if you wish. Leave blank any test you did not run.)

## H. Application implementation
Files: `app.py` (interface, forms, results, feedback, Validation Lab), `utils/prompts.py` (prompt engineering), `utils/gemini.py` (API), `utils/helpers.py` (validation, parsing, V1/V2 comparison), `requirements.txt` (`streamlit`, `google-genai`, `pandas`), `tests/` (automated tests).
Input validation: required fields, pH 0–14 (comma or point decimals), 1000-character limit, weather text not required only when the farmer says they do not know the weather. Loading spinner while Gemini responds. Feedback: 1–5 star rating and comments saved for the session and to a CSV (spreadsheet-formula characters are neutralised), downloadable from the About page. Extras: 12 answer languages, download button for each answer, sidebar API-key status.
**[YOU: insert screenshots of the landing page, dashboard, each feature page, a result, the weather warning, the Validation Lab comparison and the feedback form.]**

## I. GitHub repository details
Repository name: [ADD]  URL: [ADD]  Should contain: app.py, requirements.txt, README.md, FA2_Submission_Report.md, utils/, tests/, .streamlit/config.toml, .streamlit/secrets.toml.example, .gitignore. **[YOU: after pushing, confirm secrets.toml is NOT in the repository ✔ and attach a screenshot of the file list.]**

## J. Streamlit deployment
**[YOU: complete only after deploying.]** Steps to follow: Streamlit Community Cloud → Create app → select the repository, branch and main file `app.py` → Advanced settings → Secrets → add `GEMINI_API_KEY = "..."` → Deploy.
Public URL: [ADD]  Date deployed: [ADD]  Build result: [success / problems and fixes]

## K. Testing and results
| Device / browser | Result | Screenshot |
|---|---|---|
| [e.g. Windows laptop – Chrome] | [works / issues] | [INSERT] |
| [e.g. Android phone – Chrome] | [ ] | [INSERT] |
| [e.g. iPhone – Safari / tablet] | [ ] | [INSERT] |

Error-handling tests you should run and record: empty form [result]; pH = 20 [result]; missing API key [result]; wrong API key [result]; each of the five features [result]; two languages [result]; feedback submit and CSV download [result].

Automated checks run by the developer (fake Streamlit / mocked Gemini, **not** real runtime tests): 24 unit tests passed; page smoke test passed. Real-environment tests: **[YOU: add]**.

## L. Limitations and future improvements
Limitations: general guidance only; no live weather or soil data (weather advice depends entirely on what the farmer types); cannot confirm pests from text; possible AI mistakes or weaker translations, especially for less common languages; form fields reset when changing pages; feedback storage on Streamlit Cloud is temporary; API quota limits; automatic comparison counts in the Validation Lab are not a quality measure.
Future: weather API, image-based diagnosis, voice input, persistent database, regional datasets (FAO/KVK), SMS/offline access.

## M. Conclusion
[Write 4–5 sentences in your own words: what you built, what validation taught you about hallucination, bias and over-generalisation, and how prompt design improved the output.]
