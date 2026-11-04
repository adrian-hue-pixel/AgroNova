"""Crop calendar: what to do next, by crop and growth stage, with reminders.

Two sources of schedules:
1. Built-in generic templates for common crops (works offline). Each task is placed at a FRACTION of the crop's
   maturity time, so changing "days to harvest" stretches or shrinks the whole plan.
2. An AI-tailored schedule from Gemini for the farmer's region (validated by `tasks_from_ai`).
These are general guides, not local recommendations: sowing windows and varieties differ by region.

Reminders: in-app (due / overdue lists) and a standard .ics file that any phone calendar can import, so the
phone itself sends the reminder even when AgroNova is closed.
"""
import datetime

from utils.store import new_id

KINDS = ("plant", "water", "fertilize", "weed", "scout", "harvest", "other")
KIND_LABELS = {"plant": "Plant", "water": "Water", "fertilize": "Feed the soil", "weed": "Weed",
               "scout": "Check for pests", "harvest": "Harvest", "other": "Other"}

# (fraction of the maturity time, kind, task). No chemical doses anywhere: follow labels and local advisers.
TEMPLATES = {
    "rice": {"label": "Rice (transplanted paddy)", "maturity": 120, "aliases": ("rice", "paddy"), "tasks": [
        (0.00, "plant", "Transplant healthy seedlings and keep a thin layer of water on the field"),
        (0.06, "scout", "Fill gaps where seedlings died and check the water level"),
        (0.17, "weed", "First weeding, then add organic manure or fertilizer as your local adviser recommends"),
        (0.33, "scout", "Second weeding. Check leaves for spots, rolled leaves or stem borer damage"),
        (0.50, "water", "Keep enough water in the field during flowering; do not let it dry out"),
        (0.75, "scout", "Check grain heads for pests and disease; remove badly affected plants"),
        (0.90, "water", "Drain the field about 7-10 days before harvest so the crop ripens evenly"),
        (1.00, "harvest", "Harvest when most grains in the head have turned golden; dry the grain well before storing")]},
    "maize": {"label": "Maize (corn)", "maturity": 100, "aliases": ("maize", "corn"), "tasks": [
        (0.00, "plant", "Sow seed into moist soil at the spacing your local adviser recommends"),
        (0.10, "scout", "Check germination and re-sow gaps"),
        (0.20, "weed", "First weeding; look for fall armyworm holes in young leaves"),
        (0.35, "fertilize", "Side-dress nitrogen as advised locally when plants are knee high"),
        (0.50, "water", "Water well at tasseling and silking: this is when maize needs water most"),
        (0.70, "scout", "Check cobs for pests and mould"),
        (1.00, "harvest", "Harvest when husks are dry and kernels are hard; dry cobs before storing")]},
    "wheat": {"label": "Wheat", "maturity": 120, "aliases": ("wheat",), "tasks": [
        (0.00, "plant", "Sow into well-prepared soil with enough moisture"),
        (0.18, "water", "First irrigation at crown root stage if the soil is dry"),
        (0.30, "weed", "Weed the field while weeds are small"),
        (0.45, "water", "Irrigate at tillering / jointing if rain has not come"),
        (0.65, "water", "Irrigate at flowering and grain filling if the soil is dry"),
        (0.75, "scout", "Check leaves for rust or powdery mildew"),
        (1.00, "harvest", "Harvest when grains are hard and the straw is golden-dry")]},
    "tomato": {"label": "Tomato", "maturity": 110, "aliases": ("tomato", "tomatoes"), "tasks": [
        (0.00, "plant", "Transplant seedlings in the evening and water them in"),
        (0.10, "water", "Water regularly and evenly; avoid wetting leaves late in the day"),
        (0.20, "weed", "Weed and add mulch to hold moisture; stake or support plants"),
        (0.35, "fertilize", "Feed the soil with compost or fertilizer as your local adviser recommends"),
        (0.45, "scout", "Check leaves weekly for spots, curling or whitefly"),
        (0.60, "water", "Keep watering even through flowering and fruit set"),
        (0.75, "harvest", "Start picking ripe fruit; pick every few days")]},
    "groundnut": {"label": "Groundnut (peanut)", "maturity": 110, "aliases": ("groundnut", "peanut", "peanuts"), "tasks": [
        (0.00, "plant", "Sow seed in loose, well-drained soil"),
        (0.12, "weed", "First weeding"),
        (0.30, "weed", "Second weeding and earthing-up so pegs can enter the soil"),
        (0.45, "water", "Make sure there is enough moisture during flowering and pegging"),
        (0.65, "scout", "Check leaves for leaf spot and pests"),
        (0.90, "water", "Stop irrigating a week or so before harvest"),
        (1.00, "harvest", "Dig a few plants to check pod maturity; harvest and dry pods well")]},
    "cotton": {"label": "Cotton", "maturity": 160, "aliases": ("cotton",), "tasks": [
        (0.00, "plant", "Sow seed into moist soil"),
        (0.12, "weed", "First weeding and thinning"),
        (0.28, "fertilize", "Feed the soil as advised locally"),
        (0.35, "scout", "Start weekly checks for sucking pests and bollworm"),
        (0.50, "water", "Water at flowering and boll formation if dry"),
        (0.80, "scout", "Check bolls for damage; keep records of what you see"),
        (1.00, "harvest", "Pick open bolls on dry days; keep cotton clean and dry")]},
    "pearl millet": {"label": "Pearl millet (bajra / kambu)", "maturity": 85, "aliases": ("pearl millet", "bajra", "kambu", "millet"), "tasks": [
        (0.00, "plant", "Sow at the start of reliable rain"),
        (0.15, "weed", "Thin plants and weed"),
        (0.35, "fertilize", "Add organic manure or fertilizer as advised locally"),
        (0.55, "scout", "Check ear heads for pests and downy mildew"),
        (0.60, "water", "If there is a long dry spell at flowering, give a light irrigation if possible"),
        (1.00, "harvest", "Harvest when grains are hard and ear heads are dry")]},
    "chilli": {"label": "Chilli / pepper", "maturity": 150, "aliases": ("chilli", "chili", "chile", "pepper"), "tasks": [
        (0.00, "plant", "Transplant seedlings and water them in"),
        (0.10, "water", "Water lightly and often while young plants establish"),
        (0.20, "weed", "Weed and mulch"),
        (0.30, "fertilize", "Feed the soil as your local adviser recommends"),
        (0.40, "scout", "Weekly checks for thrips, mites and leaf curl"),
        (0.55, "harvest", "First picking of ripe fruit; continue every 1-2 weeks")]},
}
GENERIC = {"label": "Generic crop", "maturity": 100, "aliases": (), "tasks": [
    (0.00, "plant", "Plant or sow into prepared, moist soil"),
    (0.10, "scout", "Check germination and fill gaps"),
    (0.20, "weed", "First weeding"),
    (0.35, "fertilize", "Feed the soil as your local adviser recommends"),
    (0.50, "water", "Water at flowering or fruit set if the soil is dry"),
    (0.70, "scout", "Check leaves and fruit for pests and disease"),
    (1.00, "harvest", "Harvest when the crop is ripe; dry or store it carefully")]}


def match_template(crop: str) -> dict:
    name = (crop or "").strip().lower()
    for key, t in TEMPLATES.items():
        if name == key or any(a in name for a in t["aliases"]):
            return t
    return GENERIC


def stage_for(fraction: float) -> str:
    if fraction < 0:
        return "Not planted yet"
    if fraction < 0.15:
        return "Germination / seedling"
    if fraction < 0.45:
        return "Growing leaves and stems"
    if fraction < 0.70:
        return "Flowering / fruit set"
    if fraction < 0.90:
        return "Filling grain or fruit"
    if fraction <= 1.10:
        return "Ready to harvest"
    return "Past the expected harvest date"


def parse_date(value):
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def build_schedule(crop: str, planted: datetime.date, maturity: int = None) -> list:
    t = match_template(crop)
    days = int(maturity or t["maturity"])
    days = max(20, min(days, 400))
    out = []
    for frac, kind, title in t["tasks"]:
        due = planted + datetime.timedelta(days=round(frac * days))
        out.append({"id": new_id(), "crop": crop, "title": title, "kind": kind, "due": due.isoformat(), "done": False})
    return out


def tasks_from_ai(items, crop: str, planted: datetime.date, max_days: int = 400) -> list:
    """Validate a JSON list from Gemini: [{"day": 0, "kind": "plant", "title": "..."}]. Bad rows are skipped."""
    out = []
    if not isinstance(items, list):
        return out
    for it in items[:25]:
        if not isinstance(it, dict):
            continue
        try:
            day = int(it.get("day"))
        except (TypeError, ValueError):
            continue
        title = " ".join(str(it.get("title", "")).split())[:140]
        if not title or not 0 <= day <= max_days:
            continue
        kind = str(it.get("kind", "other")).lower()
        out.append({"id": new_id(), "crop": crop, "title": title, "kind": kind if kind in KINDS else "other",
                    "due": (planted + datetime.timedelta(days=day)).isoformat(), "done": False})
    return sorted(out, key=lambda t: t["due"])


def crop_progress(crop: dict, today: datetime.date) -> dict:
    """{'stage', 'pct', 'days_to_harvest', 'planted'} for one crop from the farm profile."""
    planted = parse_date(crop.get("planted"))
    maturity = int(crop.get("maturity") or match_template(crop.get("name", ""))["maturity"])
    if not planted:
        return {"stage": "Planting date not set", "pct": 0, "days_to_harvest": None, "planted": None, "maturity": maturity}
    elapsed = (today - planted).days
    frac = elapsed / maturity
    return {"stage": stage_for(frac), "pct": max(0, min(100, round(frac * 100))),
            "days_to_harvest": maturity - elapsed, "planted": planted, "maturity": maturity}


def categorize(tasks: list, today: datetime.date) -> dict:
    """Group tasks: overdue / today / week (next 7 days) / later / done. Each list is sorted by due date."""
    groups = {"overdue": [], "today": [], "week": [], "later": [], "done": []}
    for t in tasks:
        due = parse_date(t.get("due"))
        if t.get("done"):
            groups["done"].append(t)
        elif due is None:
            groups["later"].append(t)
        elif due < today:
            groups["overdue"].append(t)
        elif due == today:
            groups["today"].append(t)
        elif due <= today + datetime.timedelta(days=7):
            groups["week"].append(t)
        else:
            groups["later"].append(t)
    for g in groups.values():
        g.sort(key=lambda t: str(t.get("due")))
    return groups


def next_task_for(tasks: list, crop: str, today: datetime.date):
    pending = [t for t in tasks if t.get("crop") == crop and not t.get("done")]
    pending.sort(key=lambda t: str(t.get("due")))
    return pending[0] if pending else None


# ---------------------------------------------------------------- .ics export (RFC 5545)
def _esc(text: str) -> str:
    return (str(text).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r", "").replace("\n", "\\n"))


def _fold(line: str) -> str:
    """Lines may be at most 75 octets: fold longer ones with CRLF + space (never splitting a UTF-8 character)."""
    raw, out, cur = line.encode("utf-8"), [], b""
    limit = 75
    for ch in line:
        b = ch.encode("utf-8")
        if len(cur) + len(b) > limit:
            out.append(cur.decode("utf-8"))
            cur, limit = b"", 74
        cur += b
    out.append(cur.decode("utf-8"))
    return "\r\n ".join(out) if raw else line


def make_ics(tasks: list, farm_name: str = "My farm", now: datetime.datetime = None) -> str:
    """All not-yet-done tasks as all-day events with a reminder at 07:00 on the day."""
    stamp = (now or datetime.datetime.utcnow()).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AgroNova//Crop calendar//EN", "CALSCALE:GREGORIAN",
             f"X-WR-CALNAME:{_esc('AgroNova - ' + farm_name)}"]
    for t in tasks:
        due = parse_date(t.get("due"))
        if t.get("done") or not due:
            continue
        end = due + datetime.timedelta(days=1)
        summary = f"{t.get('crop', '')}: {t.get('title', '')}".strip(": ")
        lines += ["BEGIN:VEVENT", f"UID:{t.get('id', new_id())}@agronova", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{due.strftime('%Y%m%d')}", f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
                  f"SUMMARY:{_esc(summary)[:200]}",
                  f"DESCRIPTION:{_esc('AgroNova reminder - ' + KIND_LABELS.get(t.get('kind'), 'Task'))}",
                  "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_esc(summary)[:100]}", "TRIGGER;RELATED=START:PT7H",
                  "END:VALARM", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(l) for l in lines) + "\r\n"
