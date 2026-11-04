"""Small, reproducible live checks used by the Validation Lab."""
import datetime
import time

from utils.gemini import GeminiError, active_model, generate_advice
from utils.prompts import build_free_prompt


def run_checks(question, settings):
    """Keep the prompt constant except for the explicitly varied setting."""
    records = []
    for setting in settings:
        language = setting.get("language", "English")
        prompt = build_free_prompt(question, language, True)
        started = time.monotonic()
        record = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "model": active_model(), "question": question, "prompt_sent": prompt, **setting}
        try:
            record["answer"] = generate_advice(prompt, temperature=setting.get("temperature", 0.3),
                                                max_tokens=setting.get("max_output_tokens", 8192))
            record["error"] = None
        except GeminiError as exc:
            record["answer"], record["error"] = None, str(exc)
        record["elapsed_seconds"] = round(time.monotonic() - started, 2)
        records.append(record)
    return records
