"""Voice support: spoken answers (the browser's built-in speech synthesis) and helpers for voice questions.

Spoken answers cost no API calls and use no mobile data, because the phone or computer reads the text itself.
Which languages can be spoken depends on the voices installed on the farmer's device (Android and iOS usually
include Hindi, Tamil, etc.). If no voice matches, the page says so instead of failing silently.
Voice QUESTIONS are recorded in the app and transcribed by Gemini (see utils/gemini.transcribe_audio).
"""
import html
import json
import re

LANG_CODES = {
    "English": "en-IN", "Hindi": "hi-IN", "Tamil": "ta-IN", "Telugu": "te-IN", "Kannada": "kn-IN",
    "Malayalam": "ml-IN", "Marathi": "mr-IN", "Bengali": "bn-IN", "French": "fr-FR", "Spanish": "es-ES",
    "Portuguese": "pt-BR", "Twi (Ghana)": "ak-GH",
}


def lang_code(language: str) -> str:
    return LANG_CODES.get(language, "en-IN")


def question_language(text: str, selected: str = "English") -> str:
    """Match supported Indian scripts; Latin and ambiguous scripts use the chosen language."""
    ranges = [("Tamil", 0x0B80, 0x0BFF), ("Telugu", 0x0C00, 0x0C7F),
              ("Kannada", 0x0C80, 0x0CFF), ("Malayalam", 0x0D00, 0x0D7F),
              ("Bengali", 0x0980, 0x09FF)]
    for name, lo, hi in ranges:
        if any(lo <= ord(char) <= hi for char in text):
            return name
    if any(0x0900 <= ord(char) <= 0x097F for char in text):
        return "Marathi" if selected == "Marathi" else "Hindi"
    return selected


def strip_markdown(text: str) -> str:
    """Turn the model's Markdown into plain sentences that sound natural when read aloud."""
    text = re.sub(r"(?m)^\s*#{1,6}\s*(.+?)\s*$", r"\1.", text)          # headings become sentences
    text = re.sub(r"(?m)^\s*(?:[-*\u2022]|\d+[.)])\s+", "", text)         # list markers
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)                  # links -> their text
    text = re.sub(r"[*_`>~]+", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def speak_html(text: str, language: str, dark: bool = False, label: str = "Listen to this answer") -> str:
    """A small self-contained player (button + stop). Returns HTML for streamlit.components.v1.html()."""
    plain = strip_markdown(text)[:6000]
    payload = json.dumps(plain).replace("</", "<\\/")
    lang = json.dumps(lang_code(language))
    bg, fg, accent = ("#17181B", "#F5F5F7", "#7BD3A0") if dark else ("#FFFFFF", "#14231A", "#1B7A4B")
    btn_fg = "#06150C" if dark else "#FFFFFF"
    return f"""<div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:{fg};background:{bg};margin:0;">
<button id="play" style="background:{accent};color:{btn_fg};border:0;border-radius:999px;padding:.65rem 1.3rem;font-size:1rem;font-weight:600;cursor:pointer;">{html.escape(label)}</button>
<button id="stop" style="background:transparent;color:{fg};border:1px solid {accent};border-radius:999px;padding:.6rem 1.1rem;font-size:1rem;cursor:pointer;margin-left:.4rem;">Stop</button>
<div id="msg" style="font-size:.85rem;margin-top:.5rem;opacity:.8;"></div></div>
<script>
const TEXT={payload}, LANG={lang};
const msg=document.getElementById('msg');
function speak(){{
  if(!('speechSynthesis' in window)){{msg.textContent='This browser cannot read aloud. Try Chrome or Safari.';return;}}
  speechSynthesis.cancel();
  const voices=speechSynthesis.getVoices();
  const base=LANG.slice(0,2).toLowerCase();
  const voice=voices.find(v=>v.lang&&v.lang.toLowerCase()===LANG.toLowerCase())||voices.find(v=>v.lang&&v.lang.toLowerCase().startsWith(base));
  msg.textContent=voice?'':'No voice for this language was found on this device, so the default voice is used. You can install one in your phone settings.';
  const parts=TEXT.match(/[^.!?\\n\\u0964]+[.!?\\u0964]?/g)||[TEXT];
  parts.forEach(p=>{{ if(!p.trim())return; const u=new SpeechSynthesisUtterance(p.trim()); u.lang=LANG; if(voice)u.voice=voice; u.rate=0.95; speechSynthesis.speak(u); }});
}}
document.getElementById('play').onclick=speak;
document.getElementById('stop').onclick=()=>speechSynthesis.cancel();
</script>"""
