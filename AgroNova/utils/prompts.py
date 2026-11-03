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
4. NEVER invent weather data, forecasts, prices or statistics. You have no live weather access.
   Only use weather information the farmer typed in.
5. NEVER state an uncertain plant disease/pest diagnosis as a fact. Give possible causes, say how
   confident you are (low/medium/high), and list what the farmer can check to tell them apart.
6. NEVER give exact fertilizer or pesticide doses or mixing rates. Describe the type of input and
   say to follow the product label and local extension officer / Krishi Vigyan Kendra (India) /
   Ministry of Food and Agriculture office (Ghana) / provincial agriculture ministry (Canada).
7. Prefer low-risk, low-cost, sustainable options first. Mention protective equipment and safe
   storage if chemicals are mentioned. Do not recommend banned or highly hazardous pesticides.
8. Make clear that your answer is general guidance, not a verified local recommendation, and that
   the farmer should confirm with a local agricultural expert for important decisions.
9. If the question is not about farming, politely say you can only help with farming topics."""

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
