"""Unit tests for pure-Python helpers and prompts (no Streamlit or API needed).

Run:  python -m unittest discover -s tests -v
"""
import unittest

from utils.helpers import (compare_outputs, output_metrics, parse_ph, parse_sections, safe_csv_cell,
                           validate_inputs, validation_log_markdown)
from utils.prompts import SECTION_TITLES, SYSTEM_INSTRUCTION, build_free_prompt, build_prompt

GOOD = "\n".join(f"## {t}\n- point about {t}\n- another" for t in SECTION_TITLES)


class ParsingTests(unittest.TestCase):
    def test_parses_all_five_sections(self):
        self.assertEqual(list(parse_sections(GOOD)), SECTION_TITLES)

    def test_bold_headings_and_preamble_are_accepted(self):
        self.assertTrue(parse_sections("Hello\n" + GOOD.replace("## Precautions", "## **Precautions**")))

    def test_incomplete_or_plain_text_returns_empty(self):
        self.assertEqual(parse_sections("## Overview\nonly this"), {})
        self.assertEqual(parse_sections("just text"), {})


class ValidationTests(unittest.TestCase):
    FIELDS = [{"id": "a", "label": "A", "type": "text", "required": True},
              {"id": "ph", "label": "pH", "type": "ph"},
              {"id": "m", "label": "M", "type": "multiselect", "required": True},
              {"id": "s", "label": "Source", "type": "select"},
              {"id": "w", "label": "Weather", "type": "textarea", "required": True, "required_unless": ("s", "none")}]

    def test_required_fields(self):
        errs = validate_inputs(self.FIELDS, {"a": "  ", "ph": "", "m": [], "s": "x", "w": ""})
        self.assertEqual(len(errs), 3)

    def test_required_unless(self):
        self.assertEqual(validate_inputs(self.FIELDS, {"a": "x", "m": ["q"], "s": "none", "w": ""}), [])

    def test_ph_rules(self):
        base = {"a": "x", "m": ["q"], "s": "x", "w": "rain"}
        for good in ("6.5", "6,5", "0", "14"):
            self.assertEqual(validate_inputs(self.FIELDS, {**base, "ph": good}), [], good)
        for bad in ("abc", "15", "-1", "7.x"):
            self.assertEqual(len(validate_inputs(self.FIELDS, {**base, "ph": bad})), 1, bad)
        self.assertIsNone(parse_ph("nan-ish"))

    def test_length_limit(self):
        self.assertEqual(len(validate_inputs(self.FIELDS, {"a": "x" * 1001, "m": ["q"], "s": "x", "w": "r"})), 1)

    def test_csv_formula_injection(self):
        self.assertEqual(safe_csv_cell("=SUM(A1)"), "'=SUM(A1)")
        self.assertEqual(safe_csv_cell("good comment"), "good comment")


class PromptTests(unittest.TestCase):
    def test_context_and_language_included_and_empty_skipped(self):
        p = build_prompt("crop", {"Country": "India", "Soil pH": "", "Region": "Tamil Nadu"}, "Tamil")
        self.assertIn("Tamil Nadu", p)
        self.assertNotIn("Soil pH", p)
        self.assertIn("Write the answer in Tamil", p)
        for t in SECTION_TITLES:
            self.assertIn(f"## {t}", p)

    def test_every_language_option_reaches_the_prompt(self):
        for lang in ("Hindi", "Tamil", "French", "Twi (Ghana)"):
            self.assertIn(f"Write the answer in {lang}", build_prompt("soil", {"Crop": "maize"}, lang))
        self.assertIn("Answer in simple English", build_prompt("soil", {"Crop": "maize"}, "English"))

    def test_weather_prompt_forbids_invented_forecasts(self):
        p = build_prompt("weather", {"Region": "Punjab"}, "English")
        self.assertIn("NO live weather data", p)
        self.assertIn("not on a live forecast", p)

    def test_v1_is_raw_question_and_v2_is_engineered(self):
        self.assertEqual(build_free_prompt("q?", "English", engineered=False), "q?")
        self.assertIn("FARMER'S QUESTION: q?", build_free_prompt("q?", "English", engineered=True))

    def test_system_instruction_safety_rules(self):
        for phrase in ("NEVER invent weather", "NEVER state an uncertain", "exact fertilizer or pesticide doses"):
            self.assertIn(phrase, SYSTEM_INSTRUCTION)


class CompareTests(unittest.TestCase):
    def test_metrics(self):
        m = output_metrics(GOOD + "\nAsk your local extension officer. This may help. Use 50 kg/ha.")
        self.assertEqual(m["Follows 5-section format"], "Yes")
        self.assertEqual(m["Mentions a local expert / extension service"], "Yes")
        self.assertEqual(m["Possible exact dose (e.g. 50 kg/ha) - check manually"], "Yes")
        self.assertGreaterEqual(m["List items"], 10)

    def test_compare(self):
        r = compare_outputs("Grow millet. It might work.", GOOD)
        self.assertEqual(r["metrics"]["V1"]["Follows 5-section format"], "No")
        self.assertEqual(r["metrics"]["V2"]["Follows 5-section format"], "Yes")
        self.assertTrue(0 <= r["similarity"] <= 100)
        self.assertTrue(any("longer" in c for c in r["changes"]))

    def test_log_markdown_contains_only_supplied_data(self):
        entry = {"saved_at": "t", "run_id": 1, "test": "TEST 1", "version": "V2", "model": "m", "temperature": 0.3,
                 "language": "English", "original_prompt": "q", "prompt_sent": "p", "system_instruction_used": True,
                 "answer": "real answer", "metrics": output_metrics("real answer"), "v1_v2_similarity_percent": 40,
                 "checklist": {"Is it good?": True, "Is it safe?": False}, "notes": ""}
        md = validation_log_markdown([entry])
        self.assertIn("real answer", md)
        self.assertIn("- [x] Is it good?", md)
        self.assertIn("- [ ] Is it safe?", md)


if __name__ == "__main__":
    unittest.main()
