"""Reusable Gemini API wrapper for AgroNova (uses the current `google-genai` SDK).

Configuration summary
- API key   : read from Streamlit secrets (or an environment variable) - never written in code.
- Model     : DEFAULT_MODEL, or the optional GEMINI_MODEL secret.
- System instruction, temperature and max_output_tokens are passed in one GenerateContentConfig.
- Thinking  : Gemini 3.x models use `thinking_level`; Gemini 2.5 Flash uses `thinking_budget`.
              Passing both to a Gemini 3 model is an API error, so only one is ever sent.
- Gemini 3 features need google-genai >= 1.51.0 (see requirements.txt).
"""
import json
import os
import re

import streamlit as st
from google import genai
from google.genai import errors, types

from utils.prompts import SYSTEM_INSTRUCTION

DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_TEMPERATURE = 0.3      # low = more consistent, factual advice
# max_output_tokens also counts hidden "thinking" tokens on Gemini 3, so leave generous room
# (answers are only ~450 words; the rest is head-room for thinking).
DEFAULT_MAX_TOKENS = 8192

PLACEHOLDER_PREFIX = "paste-"  # the value used in secrets.toml.example


class GeminiError(Exception):
    """An error whose message is safe and friendly to show to a farmer."""


def _secret(name: str, default=None):
    try:
        return st.secrets[name]
    except Exception:  # no secrets file / key missing
        return os.environ.get(name, default)


def secret(name: str, default=None):
    """Public accessor for optional settings (e.g. LOCAL_SAVE, DATA_GOV_IN_API_KEY)."""
    return _secret(name, default)


def active_model() -> str:
    return str(_secret("GEMINI_MODEL", DEFAULT_MODEL))


def has_api_key() -> bool:
    key = _secret("GEMINI_API_KEY")
    return bool(key) and not str(key).startswith(PLACEHOLDER_PREFIX)


@st.cache_resource(show_spinner=False)
def _client(api_key: str):
    return genai.Client(api_key=api_key)


def thinking_config_for(model: str):
    """Return the right ThinkingConfig for the model family (or None)."""
    if model.startswith("gemini-3"):
        # LOW is supported by every Gemini 3.x Flash model; plenty for short farming advice.
        return types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW)
    if model.startswith("gemini-2.5-flash"):
        return types.ThinkingConfig(thinking_budget=0)  # turn thinking off
    return None


def build_config(model: str, system_instruction, temperature: float, max_tokens: int):
    args = dict(temperature=temperature, max_output_tokens=max_tokens)
    if system_instruction:
        args["system_instruction"] = system_instruction
    thinking = thinking_config_for(model)
    if thinking is not None:
        args["thinking_config"] = thinking
    return types.GenerateContentConfig(**args)


def friendly_error(exc: Exception, model: str) -> GeminiError:
    """Translate an SDK/network exception into a message a farmer can understand."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        msg = str(exc).lower()
        if "api key" in msg or code in (401, 403):
            return GeminiError("The Gemini API key is invalid or not allowed. Please check GEMINI_API_KEY.")
        if code == 404:
            return GeminiError(f"The model '{model}' was not found. Set GEMINI_MODEL to a model your key can use.")
        if code == 429:
            return GeminiError("Too many requests or the free quota is used up. Please wait a minute and try again.")
        if isinstance(code, int) and code >= 500:
            return GeminiError("The Gemini service is busy right now. Please try again in a moment.")
        return GeminiError("Gemini could not answer this request. Try rephrasing your question.")
    return GeminiError("Could not reach Gemini. Please check your internet connection and try again.")


def _contents(prompt, images=None, audio=None):
    """Plain text, or [photo/audio parts..., text] for multimodal requests."""
    parts = []
    for data, mime in images or []:
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))
    if audio:
        parts.append(types.Part.from_bytes(data=audio[0], mime_type=audio[1]))
    return [*parts, prompt] if parts else prompt


def extract_links(response) -> list:
    """Web pages Gemini used when Google Search grounding is on: [{'title', 'url'}] (no duplicates)."""
    links, seen = [], set()
    try:
        for chunk in response.candidates[0].grounding_metadata.grounding_chunks or []:
            web = getattr(chunk, "web", None)
            uri = getattr(web, "uri", None)
            if uri and uri not in seen:
                seen.add(uri)
                links.append({"title": getattr(web, "title", None) or uri, "url": uri})
    except (AttributeError, IndexError, TypeError):
        pass
    return links


def _run(prompt, *, system_instruction, temperature, max_tokens, images=None, audio=None, grounded=False, json_mode=False):
    """One Gemini call. Returns (text, response). Raises GeminiError with a friendly message."""
    if not has_api_key():
        raise GeminiError("The Gemini API key is not set. Add GEMINI_API_KEY to .streamlit/secrets.toml "
                          "(or to the app's Secrets on Streamlit Cloud).")
    api_key = str(_secret("GEMINI_API_KEY"))
    model = active_model()
    try:
        config = build_config(model, system_instruction, temperature, max_tokens)
        if grounded:
            config.tools = [types.Tool(google_search=types.GoogleSearch())]
        if json_mode:
            config.response_mime_type = "application/json"
        response = _client(api_key).models.generate_content(model=model, contents=_contents(prompt, images, audio),
                                                            config=config)
    except Exception as e:  # APIError, network errors, bad config ...
        raise friendly_error(e, model) from e
    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise GeminiError("Gemini returned an empty answer (it may have been blocked by a safety filter). "
                          "Please rephrase your question or try another photo.")
    return text, response


def _truncation_note(text, response):
    try:  # tell the user if the answer hit the length limit
        if "MAX_TOKENS" in str(response.candidates[0].finish_reason):
            text += "\n\n*(This answer was cut short by the length limit. Try a shorter question.)*"
    except Exception:
        pass
    return text


def generate_advice(prompt: str, *, system_instruction: str = SYSTEM_INSTRUCTION,
                    temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS,
                    images: list = None) -> str:
    """Send one prompt (optionally with photos) to Gemini and return the answer text. Raises GeminiError."""
    text, response = _run(prompt, system_instruction=system_instruction, temperature=temperature,
                          max_tokens=max_tokens, images=images)
    return _truncation_note(text, response)


def generate_with_sources(prompt: str, *, system_instruction: str = SYSTEM_INSTRUCTION,
                          temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS) -> tuple:
    """Like generate_advice, but lets Gemini check Google Search. Returns (text, [{'title','url'}])."""
    text, response = _run(prompt, system_instruction=system_instruction, temperature=temperature,
                          max_tokens=max_tokens, grounded=True)
    return _truncation_note(text, response), extract_links(response)


def transcribe_audio(audio_bytes: bytes, mime: str = "audio/wav", language: str = "English") -> str:
    """Speech to text with Gemini. Returns only what the speaker said."""
    prompt = (f"Transcribe this short voice recording of a farmer exactly as spoken. The speaker may use {language}, "
              f"English or a mix. Write the words in their original language and script. Return ONLY the transcript, "
              f"with no comments. If you hear no speech, return the single word NOSPEECH.")
    text, _ = _run(prompt, system_instruction=None, temperature=0.0, max_tokens=1024, audio=(audio_bytes, mime))
    if text.strip().upper().startswith("NOSPEECH"):
        raise GeminiError("We could not hear any speech. Please record again, closer to the microphone.")
    return text


def parse_json_loose(text: str):
    """Parse JSON even if the model wrapped it in ```json fences or added a sentence around it."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        return json.loads(cleaned)
    except ValueError:
        pass
    for open_c, close_c in (("[", "]"), ("{", "}")):
        start, end = cleaned.find(open_c), cleaned.rfind(close_c)
        if 0 <= start < end:
            try:
                return json.loads(cleaned[start:end + 1])
            except ValueError:
                continue
    raise GeminiError("Gemini's answer could not be read. Please try again.")


def generate_json(prompt: str, *, system_instruction: str = SYSTEM_INSTRUCTION, temperature: float = 0.2,
                  max_tokens: int = DEFAULT_MAX_TOKENS, images: list = None):
    """Ask for JSON and return the parsed Python object. Raises GeminiError."""
    text, _ = _run(prompt, system_instruction=system_instruction, temperature=temperature, max_tokens=max_tokens,
                   images=images, json_mode=True)
    return parse_json_loose(text)
