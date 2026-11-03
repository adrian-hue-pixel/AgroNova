"""Reusable Gemini API wrapper for AgroNova (uses the current `google-genai` SDK).

Configuration summary
- API key   : read from Streamlit secrets (or an environment variable) - never written in code.
- Model     : DEFAULT_MODEL, or the optional GEMINI_MODEL secret.
- System instruction, temperature and max_output_tokens are passed in one GenerateContentConfig.
- Thinking  : Gemini 3.x models use `thinking_level`; Gemini 2.5 Flash uses `thinking_budget`.
              Passing both to a Gemini 3 model is an API error, so only one is ever sent.
- Gemini 3 features need google-genai >= 1.51.0 (see requirements.txt).
"""
import os

import streamlit as st
from google import genai
from google.genai import errors, types

from utils.prompts import SYSTEM_INSTRUCTION

DEFAULT_MODEL = "gemini-3.8-flash"
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


def generate_advice(prompt: str, *, system_instruction: str = SYSTEM_INSTRUCTION,
                    temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    """Send one prompt to Gemini and return the answer text. Raises GeminiError with a friendly message."""
    if not has_api_key():
        raise GeminiError("The Gemini API key is not set. Add GEMINI_API_KEY to .streamlit/secrets.toml "
                          "(or to the app's Secrets on Streamlit Cloud).")
    api_key = str(_secret("GEMINI_API_KEY"))
    model = active_model()
    try:
        config = build_config(model, system_instruction, temperature, max_tokens)
        response = _client(api_key).models.generate_content(model=model, contents=prompt, config=config)
    except Exception as e:  # APIError, network errors, bad config ...
        raise friendly_error(e, model) from e

    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise GeminiError("Gemini returned an empty answer (it may have been blocked by a safety filter). "
                          "Please rephrase your question.")
    try:  # tell the user if the answer hit the length limit
        reason = str(response.candidates[0].finish_reason)
        if "MAX_TOKENS" in reason:
            text += "\n\n*(This answer was cut short by the length limit. Try a shorter question.)*"
    except Exception:
        pass
    return text
