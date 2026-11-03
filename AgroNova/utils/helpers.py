"""Small pure-Python helpers (no Streamlit / API code, so they are easy to test)."""
import difflib
import re

from utils.prompts import SECTION_TITLES

MAX_TEXT_LENGTH = 1000


def parse_sections(text: str) -> dict:
    """Split Gemini's Markdown into {section title: body}. Returns {} if the format was not followed."""
    parts = re.split(r"(?m)^##\s+(.+?)\s*$", text.strip())
    # parts = [preamble, title1, body1, title2, body2, ...]
    found = {}
    for i in range(1, len(parts) - 1, 2):
        title = parts[i].strip().strip("*#: ").lower()
        for official in SECTION_TITLES:
            if title == official.lower():
                found[official] = parts[i + 1].strip()
    return found if all(t in found for t in SECTION_TITLES) else {}


def parse_ph(value):
    """Return pH as float (accepts '6,5' or '6.5'), or None if invalid / out of 0-14."""
    try:
        ph = float(str(value).strip().replace(",", "."))
    except ValueError:
        return None
    return ph if 0 <= ph <= 14 else None


def validate_inputs(fields: list, values: dict) -> list:
    """Return a list of friendly error messages (empty list = all good)."""
    errors = []
    for f in fields:
        value = values.get(f["id"])
        label = f["label"]
        empty = value in ("", None, []) or (isinstance(value, str) and not value.strip())
        unless = f.get("required_unless")  # (other_field_id, value): not required when that field has that value
        exempt = bool(unless) and values.get(unless[0]) == unless[1]
        if f.get("required") and empty and not exempt:
            errors.append(f"Please fill in: {label}.")
            continue
        if empty:
            continue
        if isinstance(value, str) and len(value) > MAX_TEXT_LENGTH:
            errors.append(f"'{label}' is too long (maximum {MAX_TEXT_LENGTH} characters).")
        if f["type"] == "ph" and parse_ph(value) is None:
            errors.append("Soil pH must be a number between 0 and 14 (for example 6.5).")
    return errors


def safe_csv_cell(value) -> str:
    """Stop spreadsheet formula injection: a cell starting with = + - @ would be run by Excel."""
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


# ------------------------------------------------------------------ Validation Lab: comparing outputs
LIST_ITEM = re.compile(r"(?m)^\s*(?:\d+[.)]|[-*\u2022])\s+")
EXPERT = re.compile(r"extension|expert|officer|KVK|Krishi|ministry|agricultur\w*\s+(?:office|authority|department|adviser|advisor)", re.I)
HEDGE = re.compile(r"\b(may|might|could|possible|possibly|likely|not sure|uncertain|unsure)\b", re.I)
DOSE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:kg|g|ml|l|litres?|liters?)\s?(?:/|per)\s?(?:ha|hectare|acre|l|litre|liter)\b", re.I)


def output_metrics(text: str) -> dict:
    """Simple, objective counts about one answer. These are NOT a quality score."""
    return {
        "Words": len(text.split()),
        "List items": len(LIST_ITEM.findall(text)),
        "Follows 5-section format": "Yes" if parse_sections(text) else "No",
        "Mentions a local expert / extension service": "Yes" if EXPERT.search(text) else "No",
        "Uncertainty words (may, might, possible...)": len(HEDGE.findall(text)),
        "Possible exact dose (e.g. 50 kg/ha) - check manually": "Yes" if DOSE.search(text) else "No",
    }


def compare_outputs(v1: str, v2: str) -> dict:
    """Compare a basic (V1) and an engineered (V2) answer. Returns metrics, similarity % and plain-English changes."""
    m1, m2 = output_metrics(v1), output_metrics(v2)
    similarity = round(difflib.SequenceMatcher(None, v1, v2).ratio() * 100)
    changes = []
    diff_words = m2["Words"] - m1["Words"]
    changes.append(f"V2 is {abs(diff_words)} words {'longer' if diff_words > 0 else 'shorter'} than V1." if diff_words
                   else "V1 and V2 have the same number of words.")
    for key in ("Follows 5-section format", "Mentions a local expert / extension service"):
        if m1[key] != m2[key]:
            changes.append(f"{key}: V1 = {m1[key]}, V2 = {m2[key]}.")
    if m1["List items"] != m2["List items"]:
        changes.append(f"List items: V1 = {m1['List items']}, V2 = {m2['List items']}.")
    if m1["Uncertainty words (may, might, possible...)"] != m2["Uncertainty words (may, might, possible...)"]:
        changes.append("Uncertainty wording: V1 = %d, V2 = %d." % (m1["Uncertainty words (may, might, possible...)"],
                                                                   m2["Uncertainty words (may, might, possible...)"]))
    dose_key = "Possible exact dose (e.g. 50 kg/ha) - check manually"
    if m1[dose_key] != m2[dose_key]:
        changes.append(f"Possible exact dose: V1 = {m1[dose_key]}, V2 = {m2[dose_key]}.")
    return {"metrics": {"V1": m1, "V2": m2}, "similarity": similarity, "changes": changes}


def validation_log_markdown(log: list) -> str:
    """Turn saved Validation Lab entries into a Markdown document (only real, saved results)."""
    out = ["# AgroNova validation log",
           "",
           "Generated by the AgroNova Validation Lab. Every answer below was returned by the Gemini API when the test was run.",
           "Metrics are simple automatic counts, not a quality score."]
    for n, e in enumerate(log, 1):
        out += ["", f"## Entry {n}: {e['test']} - {e['version']}", "",
                f"- Saved at: {e['saved_at']}", f"- Model: {e['model']}", f"- Temperature: {e['temperature']}",
                f"- Answer language: {e['language']}",
                f"- System instruction used: {'yes' if e['system_instruction_used'] else 'no'}"]
        if e.get("v1_v2_similarity_percent") is not None:
            out.append(f"- V1/V2 text similarity: {e['v1_v2_similarity_percent']}%")
        out += ["", "**Original prompt:**", "", f"> {e['original_prompt']}", "",
                "**Prompt actually sent:**", "", "```", e["prompt_sent"], "```", "",
                "**Gemini response:**", "", e["answer"], "", "**Automatic metrics:**", ""]
        out += [f"- {k}: {v}" for k, v in e["metrics"].items()]
        out += ["", "**Feedback checklist:**", ""]
        out += [f"- [{'x' if v else ' '}] {k}" for k, v in e["checklist"].items()]
        out += ["", "**Notes / validation comments:**", "", e["notes"] or "(none)"]
    return "\n".join(out) + "\n"
