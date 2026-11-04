"""Saving the farmer's data: farm profile, crop calendar tasks, journal, saved advice and prices.

Where does the data live?
- During a visit: in Streamlit's session state (`st.session_state["farm"]`).
- To keep it between visits, there are two options:
  1. "My farm file": the farmer downloads a small .json backup and loads it next time (works on Streamlit Cloud,
     and the farmer keeps control of their own data).
  2. Automatic local saving to data/farm_data.json - ONLY when LOCAL_SAVE = "true" is set in the secrets.
     Use this when AgroNova runs on one device (a laptop at a co-operative, a Raspberry Pi). It is OFF by default,
     because on a shared public server one file would be shared by every visitor.

Pure Python (plus Pillow for photos), so it is unit-tested without Streamlit.
"""
import base64
import copy
import datetime
import io
import json
import uuid
from pathlib import Path

FARM_VERSION = 2
LOCAL_FILE = Path(__file__).resolve().parent.parent / "data" / "farm_data.json"
MAX_ADVICE = 30
MAX_JOURNAL = 300
MAX_TASKS = 400

PROFILE_DEFAULTS = {"name": "", "country": "India", "region": "", "place": "", "lat": None, "lon": None,
                    "timezone": "", "soil": "Not sure", "ph": "", "water": "Moderate", "land_size": "",
                    "crops": []}   # crops: [{"name", "planted": "YYYY-MM-DD" | "", "area": "", "maturity": int | None}]


def new_id() -> str:
    return uuid.uuid4().hex[:8]


def new_farm() -> dict:
    return {"version": FARM_VERSION, "profile": copy.deepcopy(PROFILE_DEFAULTS), "prefs": {}, "tasks": [],
            "journal": [], "advice": [], "prices": [], "weather": None}


def to_json(farm: dict) -> str:
    return json.dumps(farm, indent=2, ensure_ascii=False)


def from_json(text: str) -> dict:
    """Load a farm file. Unknown keys are dropped and missing ones filled, so older/odd files cannot crash the app."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError) as e:
        raise ValueError("This file is not a valid AgroNova farm file.") from e
    if not isinstance(data, dict) or "profile" not in data:
        raise ValueError("This file is not a valid AgroNova farm file.")
    farm = new_farm()
    prof = data.get("profile") if isinstance(data.get("profile"), dict) else {}
    for k in PROFILE_DEFAULTS:
        if k in prof:
            farm["profile"][k] = prof[k]
    farm["profile"]["crops"] = [c for c in farm["profile"]["crops"] if isinstance(c, dict) and str(c.get("name", "")).strip()]
    for key, cap in (("tasks", MAX_TASKS), ("journal", MAX_JOURNAL), ("advice", MAX_ADVICE), ("prices", 500)):
        items = data.get(key)
        farm[key] = [i for i in items if isinstance(i, dict)][:cap] if isinstance(items, list) else []
    if isinstance(data.get("prefs"), dict):
        farm["prefs"] = data["prefs"]
    if isinstance(data.get("weather"), dict) and "daily" in data["weather"]:
        farm["weather"] = data["weather"]
    return farm


# ---------------------------------------------------------------- optional automatic local saving
def load_local(path: Path = LOCAL_FILE):
    try:
        return from_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save_local(farm: dict, path: Path = LOCAL_FILE) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(to_json(farm), encoding="utf-8")
        return True
    except OSError:
        return False


# ---------------------------------------------------------------- photos
def _open_image(data: bytes):
    try:
        from PIL import Image, ImageOps
        img = Image.open(io.BytesIO(data))
        img = ImageOps.exif_transpose(img)
        return img.convert("RGB")
    except Exception as e:  # noqa: BLE001 - any decoding problem means "not a usable image"
        raise ValueError("This file could not be read as a photo. Please use a JPG, PNG or WEBP image.") from e


def prepare_image(data: bytes, max_px: int = 1024, quality: int = 82) -> tuple:
    """Shrink a photo before sending it to Gemini (faster, cheaper, kinder to weak connections)."""
    img = _open_image(data)
    img.thumbnail((max_px, max_px))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue(), "image/jpeg"


def make_thumbnail(data: bytes, max_px: int = 360) -> str:
    """Small base64 JPEG for the journal (kept inside the farm file)."""
    raw, _ = prepare_image(data, max_px=max_px, quality=70)
    return base64.b64encode(raw).decode("ascii")


def thumbnail_bytes(b64: str) -> bytes:
    try:
        return base64.b64decode(b64)
    except (ValueError, TypeError):
        return b""


# ---------------------------------------------------------------- collections
def add_advice(farm: dict, feature: str, title: str, text: str, language: str, links: list = None, now=None) -> dict:
    item = {"id": new_id(), "time": (now or datetime.datetime.now()).isoformat(timespec="minutes"), "feature": feature,
            "title": title, "text": text, "language": language, "links": links or []}
    farm["advice"].insert(0, item)
    del farm["advice"][MAX_ADVICE:]
    return item


def add_journal(farm: dict, entry: dict) -> dict:
    entry = dict(entry, id=new_id())
    farm["journal"].insert(0, entry)
    del farm["journal"][MAX_JOURNAL:]
    return entry


def delete_by_id(items: list, item_id: str) -> None:
    items[:] = [i for i in items if i.get("id") != item_id]


def journal_csv_rows(journal: list) -> list:
    cols = ("date", "crop", "kind", "note", "treatment", "weather", "qty", "qty_unit", "cost")
    return [{c: j.get(c, "") for c in cols} for j in journal]


def harvest_totals(journal: list) -> dict:
    """{crop: {unit: total}} from journal entries of kind 'Harvest' that have a quantity."""
    totals = {}
    for j in journal:
        if j.get("kind") != "Harvest":
            continue
        try:
            qty = float(j.get("qty") or 0)
        except (TypeError, ValueError):
            continue
        if qty <= 0:
            continue
        crop = (j.get("crop") or "Unknown").strip() or "Unknown"
        unit = j.get("qty_unit") or "kg"
        totals.setdefault(crop, {}).setdefault(unit, 0.0)
        totals[crop][unit] += qty
    return totals
