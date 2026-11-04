"""MOCKED tests for utils/gemini.py.

Streamlit and the Google GenAI SDK are replaced with tiny fakes, so these tests check OUR logic
(key handling, config building, error translation) but do NOT prove the real SDK or API works.
Run:  python -m unittest discover -s tests -v
"""
import importlib
import os
import sys
import types as pytypes
import unittest


def install_fakes():
    st = pytypes.ModuleType("streamlit")
    st.secrets = {}
    st.cache_resource = lambda *a, **k: (lambda f: f)

    class APIError(Exception):
        def __init__(self, code, message):
            super().__init__(message)
            self.code = code

    class Cfg:
        def __init__(self, **kw):
            self.kw = kw

    class ThinkingConfig(Cfg):
        pass

    class ThinkingLevel:
        LOW = "LOW"

    class Client:
        last = None

        def __init__(self, api_key):
            self.api_key = api_key
            self.models = self
            Client.last = self
            self.response = None
            self.raise_exc = None

        def generate_content(self, model, contents, config):
            self.called = dict(model=model, contents=contents, config=config)
            if Client.raise_exc:
                raise Client.raise_exc
            return Client.response

    Client.response = None
    Client.raise_exc = None
    genai = pytypes.ModuleType("google.genai")
    genai.Client = Client
    genai_types = pytypes.ModuleType("google.genai.types")
    class Part:
        @staticmethod
        def from_bytes(data, mime_type):
            return ("part", mime_type, data)

    class Tool(Cfg):
        pass

    class GoogleSearch:
        pass

    genai_types.Part, genai_types.Tool, genai_types.GoogleSearch = Part, Tool, GoogleSearch
    genai_types.GenerateContentConfig = Cfg
    genai_types.ThinkingConfig = ThinkingConfig
    genai_types.ThinkingLevel = ThinkingLevel
    genai_errors = pytypes.ModuleType("google.genai.errors")
    genai_errors.APIError = APIError
    genai.types, genai.errors = genai_types, genai_errors
    google = pytypes.ModuleType("google")
    google.genai = genai
    sys.modules.update({"streamlit": st, "google": google, "google.genai": genai,
                        "google.genai.types": genai_types, "google.genai.errors": genai_errors})
    return st, Client, APIError


class Resp:
    def __init__(self, text, finish="STOP"):
        self.text = text
        self.candidates = [pytypes.SimpleNamespace(finish_reason=finish)]


class GeminiLogicTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("GEMINI_MODEL", None)
        self.st, self.Client, self.APIError = install_fakes()
        sys.modules.pop("utils.gemini", None)
        self.g = importlib.import_module("utils.gemini")

    def test_default_model(self):
        self.assertEqual(self.g.DEFAULT_MODEL, "gemini-3.5-flash-lite")
        self.assertEqual(self.g.active_model(), "gemini-3.5-flash-lite")

    def test_model_override_from_secrets(self):
        self.st.secrets["GEMINI_MODEL"] = "gemini-3.7-flash"
        self.assertEqual(self.g.active_model(), "gemini-3.7-flash")

    def test_missing_and_placeholder_keys(self):
        self.assertFalse(self.g.has_api_key())
        self.st.secrets["GEMINI_API_KEY"] = "paste-your-key-from-Google-AI-Studio-here"
        self.assertFalse(self.g.has_api_key())
        with self.assertRaises(self.g.GeminiError):
            self.g.generate_advice("hi")

    def test_thinking_config_per_model_family(self):
        t3 = self.g.thinking_config_for("gemini-3.8-flash").kw
        self.assertEqual(t3, {"thinking_level": "LOW"})           # never also thinking_budget
        t25 = self.g.thinking_config_for("gemini-2.5-flash").kw
        self.assertEqual(t25, {"thinking_budget": 0})
        self.assertIsNone(self.g.thinking_config_for("something-else"))

    def test_config_has_system_instruction_temperature_and_tokens(self):
        cfg = self.g.build_config("gemini-3.8-flash", "SYS", 0.3, 8192).kw
        self.assertEqual((cfg["system_instruction"], cfg["temperature"], cfg["max_output_tokens"]), ("SYS", 0.3, 8192))
        self.assertNotIn("system_instruction", self.g.build_config("gemini-3.8-flash", None, 0.3, 100).kw)

    def test_successful_call(self):
        self.st.secrets["GEMINI_API_KEY"] = "real-looking-key"
        self.Client.response = Resp("  hello farmer  ")
        self.assertEqual(self.g.generate_advice("q"), "hello farmer")
        called = self.Client.last.called
        self.assertEqual(called["model"], "gemini-3.5-flash-lite")
        self.assertEqual(called["config"].kw["temperature"], 0.3)
        self.assertEqual(called["config"].kw["max_output_tokens"], 8192)

    def test_truncation_note_and_empty_answer(self):
        self.st.secrets["GEMINI_API_KEY"] = "k"
        self.Client.response = Resp("partial", finish="FinishReason.MAX_TOKENS")
        self.assertIn("cut short", self.g.generate_advice("q"))
        self.Client.response = Resp("")
        with self.assertRaises(self.g.GeminiError):
            self.g.generate_advice("q")

    def test_error_translation(self):
        self.st.secrets["GEMINI_API_KEY"] = "k"
        cases = [(self.APIError(400, "API key not valid"), "invalid"), (self.APIError(403, "denied"), "invalid"),
                 (self.APIError(404, "no model"), "not found"), (self.APIError(429, "quota"), "quota"),
                 (self.APIError(503, "down"), "busy"), (self.APIError(400, "bad"), "rephras"),
                 (ConnectionError("offline"), "internet")]
        for exc, word in cases:
            self.Client.raise_exc = exc
            with self.assertRaises(self.g.GeminiError) as ctx:
                self.g.generate_advice("q")
            self.assertIn(word, str(ctx.exception).lower(), exc)
        self.Client.raise_exc = None

    # ---------------------------------------------------------------- v2: photos, audio, JSON, search links
    def test_photo_is_sent_as_a_part_before_the_text(self):
        self.st.secrets["GEMINI_API_KEY"] = "k"
        self.Client.response = Resp("ok")
        self.g.generate_advice("what is this?", images=[(b"JPEGDATA", "image/jpeg")])
        contents = self.Client.last.called["contents"]
        self.assertEqual(contents[0], ("part", "image/jpeg", b"JPEGDATA"))
        self.assertEqual(contents[1], "what is this?")

    def test_plain_prompt_stays_a_plain_string(self):
        self.st.secrets["GEMINI_API_KEY"] = "k"
        self.Client.response = Resp("ok")
        self.g.generate_advice("hello")
        self.assertEqual(self.Client.last.called["contents"], "hello")

    def test_json_mode_and_loose_parsing(self):
        self.st.secrets["GEMINI_API_KEY"] = "k"
        self.Client.response = Resp('```json\n[{"question": "Q", "options": ["a", "b"]}]\n```')
        out = self.g.generate_json("make questions")
        self.assertEqual(out[0]["question"], "Q")
        self.assertEqual(self.Client.last.called["config"].response_mime_type, "application/json")
        self.assertEqual(self.g.parse_json_loose('Sure! Here: {"a": 1} hope it helps'), {"a": 1})
        with self.assertRaises(self.g.GeminiError):
            self.g.parse_json_loose("no json here")

    def test_transcribe_audio(self):
        self.st.secrets["GEMINI_API_KEY"] = "k"
        self.Client.response = Resp("  when to sow paddy  ")
        self.assertEqual(self.g.transcribe_audio(b"WAV", "audio/wav", "Tamil"), "when to sow paddy")
        self.assertEqual(self.Client.last.called["contents"][0], ("part", "audio/wav", b"WAV"))
        self.Client.response = Resp("NOSPEECH")
        with self.assertRaises(self.g.GeminiError):
            self.g.transcribe_audio(b"WAV")

    def test_grounded_call_returns_unique_web_links(self):
        self.st.secrets["GEMINI_API_KEY"] = "k"
        web = lambda u, t: pytypes.SimpleNamespace(web=pytypes.SimpleNamespace(uri=u, title=t))
        resp = Resp("advice")
        resp.candidates[0].grounding_metadata = pytypes.SimpleNamespace(
            grounding_chunks=[web("https://a.example/x", "A"), web("https://a.example/x", "A again"), web("https://b.example", None)])
        self.Client.response = resp
        text, links = self.g.generate_with_sources("q")
        self.assertEqual(text, "advice")
        self.assertEqual([l["url"] for l in links], ["https://a.example/x", "https://b.example"])
        self.assertTrue(self.Client.last.called["config"].tools)


if __name__ == "__main__":
    unittest.main()
