"""Prompt engineering for AgroNova.

Every prompt = SYSTEM_INSTRUCTION (role + safety rules, sent separately)
             + task instruction for the chosen feature
             + the farmer's context (location, crop, soil, season ...)
             + a fixed OUTPUT_FORMAT so the app can display the answer in clear sections.
"""

SECTION_TITLES = [
    "Overview",
    "Recommended Actions",
    "Why These Recommendations",
    "Precautions",
    "Additional Suggestions",
]

SYSTEM_INSTRUCTION = """You are AgroNova, a careful and friendly agricultural advisor for small and medium-scale farmers
in India, Ghana, Canada and other countries.

RULES YOU MUST FOLLOW
1. Use very simple words. Short sentences. The reader may have limited formal education.
2. Always tailor advice to the farmer's stated country, region, crop, soil, season and water situation.
   If an important detail is missing, say what you assumed.
3. Explain WHY for every recommendation.
4. NEVER invent weather data, forecasts, prices or statistics. You have no live weather access of your own.
   Only use weather information given in the prompt: either typed by the farmer, or supplied by the app
   from a weather service (marked "LIVE FORECAST"). Only use prices the farmer or app gave you.
5. NEVER state an uncertain plant disease/pest diagnosis as a fact. Give possible causes, say how
   confident you are (low/medium/high), and list what the farmer can check to tell them apart.
6. NEVER give exact fertilizer or pesticide doses or mixing rates. Describe the type of input and
   say to follow the product label and local extension officer / Krishi Vigyan Kendra (India) /
   Ministry of Food and Agriculture office (Ghana) / provincial agriculture ministry (Canada).
7. Prefer low-risk, low-cost, sustainable options first. Mention protective equipment and safe
   storage if chemicals are mentioned. Do not recommend banned or highly hazardous pesticides.
8. Make clear that your answer is general guidance, not a verified local recommendation, and that
   the farmer should confirm with a local agricultural expert for important decisions.
9. If the question is not about farming, politely say you can only help with farming topics.
10. If a photo is provided, describe what you can actually see, say how sure you are, and say what you cannot tell
    from a photo. Never claim a certain diagnosis from a photo. If the photo is not a plant or is too unclear, say so."""

OUTPUT_FORMAT = """Write your answer in Markdown using EXACTLY these five headings, in this order,
each on its own line starting with '## ' (keep the heading words in English):

## Overview
(2-3 short sentences summarising the situation and the main advice)

## Recommended Actions
(a numbered list; each item = a bold action name, then one short line saying how to do it)

## Why These Recommendations
(bullet points that explain the reasoning behind each action, linked to the farmer's region, soil, season or crop)

## Precautions
(bullet points: safety, uncertainty, things to avoid, and when to call a local agricultural expert)

## Additional Suggestions
(2-4 bullet points of useful extras, ending with 2 follow-up questions the farmer could ask next)

Keep the whole answer under about 450 words."""

TASKS = {
    "crop": "Recommend 3-5 suitable crops for the farmer's conditions and explain why each one suits them.",
    "pest": ("Help the farmer understand a possible pest or disease problem. List the most likely causes "
             "(with a confidence level), what to check to confirm, preventive measures, and treatment options "
             "that match the farmer's preference (organic or conventional). Do NOT present a diagnosis as certain."),
    "weather": ("Give farming advice based ONLY on the weather information the farmer typed in (shown below, with the "
                "source the farmer says it came from). You have NO live weather data: do not add any forecast, "
                "temperature or rainfall prediction of your own. Begin the Overview with the sentence: 'This advice is "
                "based on the weather you reported, not on a live forecast.' If the farmer says they do not know the "
                "weather, give only general preparedness advice and tell them to check their national weather service. "
                "Cover irrigation, harvesting precautions, planting timing and weather-related risks."),
    "soil": ("Explain how suitable the soil is for the crop, what nutrients the crop needs, and how to manage soil "
             "and fertilizer. Give types of fertilizer or organic matter and how often to review, but NO exact doses."),
    "sustainable": ("Give practical sustainable-farming tips for the farmer's context: water conservation, organic "
                    "practices, natural pest management, crop rotation and soil conservation (as relevant to the "
                    "topics selected)."),
}


def language_rule(language: str) -> str:
    if language.lower() == "english":
        return "Answer in simple English."
    return (f"Write the answer in {language}, in simple everyday words. Keep the five '## ' heading lines in "
            f"English exactly as given so the app can format them, but write everything under each heading in "
            f"{language}. Crop and chemical names may also be given in English in brackets.")


def build_prompt(feature_key: str, context: dict, language: str) -> str:
    """context = {"Label shown to farmer": "value", ...} (empty values are skipped)."""
    lines = [f"- {label}: {value}" for label, value in context.items() if value not in ("", None, [])]
    farmer_block = "\n".join(lines) if lines else "- (no details given)"
    return (f"TASK: {TASKS[feature_key]}\n\n"
            f"FARMER'S SITUATION:\n{farmer_block}\n\n"
            f"LANGUAGE: {language_rule(language)}\n\n"
            f"FORMAT:\n{OUTPUT_FORMAT}")


def build_free_prompt(question: str, language: str, engineered: bool = True) -> str:
    """Used by the Validation Lab. V1 = raw question only, V2 = engineered prompt."""
    if not engineered:
        return question
    return (f"TASK: Answer the farmer's question with region-specific, practical advice.\n\n"
            f"FARMER'S QUESTION: {question}\n\n"
            f"LANGUAGE: {language_rule(language)}\n\n"
            f"FORMAT:\n{OUTPUT_FORMAT}")


# ---------------------------------------------------------------- personalisation (language is handled above)
DETAIL_LEVELS = {
    "Short and simple": "Keep the whole answer under about 180 words. Give at most 3 actions. Use the simplest words.",
    "Standard": "Keep the whole answer under about 450 words.",
    "Detailed": "You may use up to about 800 words. Give more reasons, alternatives and things to watch for.",
}
DEFAULT_DETAIL = "Standard"


def output_format(detail: str = DEFAULT_DETAIL) -> str:
    """The five-heading format, with the length limit that matches the farmer's chosen level of detail."""
    base = OUTPUT_FORMAT.rsplit("Keep the whole answer", 1)[0]
    return base + DETAIL_LEVELS.get(detail, DETAIL_LEVELS[DEFAULT_DETAIL])


def style_rules(detail: str = DEFAULT_DETAIL, units_rule: str = "") -> str:
    parts = [DETAIL_LEVELS.get(detail, DETAIL_LEVELS[DEFAULT_DETAIL])]
    if units_rule:
        parts.append(units_rule + " Convert any numbers you mention to these units.")
    return " ".join(parts)


def _block(label: str, body: str) -> str:
    return f"{label}:\n{body}\n\n" if body else ""


def build_prompt_v2(feature_key: str, context: dict, language: str, detail: str = DEFAULT_DETAIL, units_rule: str = "",
                    extra: str = "") -> str:
    """Same as build_prompt, plus the farmer's chosen detail level, units, and extra facts (forecast, profile)."""
    lines = [f"- {label}: {value}" for label, value in context.items() if value not in ("", None, [])]
    farmer_block = "\n".join(lines) if lines else "- (no details given)"
    return (f"TASK: {TASKS[feature_key]}\n\n"
            f"FARMER'S SITUATION:\n{farmer_block}\n\n"
            f"{_block('EXTRA FACTS PROVIDED BY THE APP (use these, do not invent others)', extra)}"
            f"STYLE: {style_rules(detail, units_rule)}\n\n"
            f"LANGUAGE: {language_rule(language)}\n\n"
            f"FORMAT:\n{output_format(detail)}")


TASKS.update({
    "forecast": ("Give farming advice for the next 7 days using ONLY the live forecast supplied by the app below (it comes "
                 "from a weather service). Do not add any weather numbers of your own. Cover watering, spraying, planting "
                 "and harvest decisions for the farmer's crops, day by day where it matters (for example 'Thursday'). "
                 "Begin the Overview with: 'This advice uses the live forecast fetched by AgroNova.'"),
    "ask": ("Answer the farmer's question with practical, region-specific advice, using the farm profile and any forecast "
            "provided. If the question needs details you do not have, say what you assumed."),
    "doctor": ("Help the farmer understand a possible plant pest or disease problem, using the symptoms, the farmer's answers "
               "to follow-up questions, and the photo if one is provided. List the most likely causes with a confidence level "
               "(low/medium/high) and why, what to check to tell them apart, prevention, and treatment options that match the "
               "farmer's preference. Do NOT present a diagnosis as certain."),
    "market": ("Comment on the crop comparison below. The prices and costs were entered by the farmer or came from a market "
               "price service: do not invent or change any numbers. Explain the main risks and benefits of each option "
               "(water needs, season, price swings, labour, storage, selling distance) and which questions to ask a local "
               "buyer or extension officer before deciding."),
})


def build_question_prompt(crop: str, region: str, symptoms: str, parts: str, language: str, has_photo: bool) -> str:
    """Step 1 of the Plant Doctor: ask Gemini for 3-5 smart follow-up questions (as JSON)."""
    photo = "A photo of the plant is attached. " if has_photo else ""
    return (f"A farmer needs help with a sick plant. {photo}Crop: {crop}. Region: {region or 'not stated'}. "
            f"Affected parts: {parts or 'not stated'}. Symptoms described: {symptoms or 'none given'}.\n\n"
            "Before suggesting any cause, ask 3 to 5 short follow-up questions whose answers would best separate the likely "
            "causes (for example: where on the plant it started, how fast it spreads, whether leaves are wet or dry, "
            "recent weather or watering, whether insects are visible, how many plants are affected). "
            "Each question must be answerable by tapping one option.\n\n"
            f"Write the questions and options in {language}, in very simple words. "
            'Return ONLY JSON: a list like [{"question": "...", "options": ["...", "...", "Not sure"]}]. '
            "Give 2 to 4 options per question and always include a 'Not sure' option (translated).")


def parse_questions(items) -> list:
    """Validate the model's JSON so a bad answer can never break the page. Returns [{'question', 'options'}]."""
    if isinstance(items, dict):
        items = items.get("questions", [])
    out = []
    if not isinstance(items, list):
        return out
    for it in items[:5]:
        if not isinstance(it, dict):
            continue
        q = " ".join(str(it.get("question", "")).split())[:200]
        opts = [" ".join(str(o).split())[:80] for o in (it.get("options") or []) if str(o).strip()][:5]
        if q and len(opts) >= 2:
            out.append({"question": q, "options": opts})
    return out


def build_calendar_prompt(crop: str, region: str, planting_date: str, maturity: int) -> str:
    return (f"Make a simple crop calendar for a small farmer. Crop: {crop}. Region: {region or 'not stated'}. "
            f"Planting date: {planting_date}. Expected days from planting to harvest: {maturity}.\n"
            "List 8 to 12 tasks covering watering, weeding, feeding the soil (NO doses), checking for pests, and harvest, "
            "each with the number of days AFTER planting when it should be done. Use simple words; write the titles in English. "
            'Return ONLY JSON: [{"day": 0, "kind": "plant|water|fertilize|weed|scout|harvest|other", "title": "short task"}]. '
            "Do not include any chemical product names or doses.")
