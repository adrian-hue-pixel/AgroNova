"""The "offline pack": ONE self-contained HTML file with the farmer's saved advice, tasks, forecast and the key
guides. It opens in any phone or computer browser with no internet, no app and no AI call.
(A web app running on a server cannot itself work without a connection - this file is the offline copy.)
"""
import datetime
import html
import re

from utils import farmcal, weather
from utils.guides import GUIDES

CSS = ("body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#F4F8F3;color:#14231A;line-height:1.55}"
       "main{max-width:760px;margin:auto;padding:1rem 1rem 3rem}h1{margin:.2rem 0}h2{margin-top:2rem;border-bottom:2px solid #CFE3D5;padding-bottom:.3rem}"
       "section,.card{background:#fff;border:1px solid #E3E8DF;border-radius:14px;padding:.9rem 1.1rem;margin:.7rem 0}"
       ".muted{color:#556459;font-size:.9rem}.warn{background:#FFF7E6;border-color:#F0D9A5}li{margin:.25rem 0}"
       ".day{display:inline-block;min-width:8.5rem;margin:.2rem;padding:.4rem .6rem;background:#EEF6F0;border-radius:10px;font-size:.9rem}")


def md_to_html(text: str) -> str:
    """A tiny, safe Markdown subset (headings, lists, bold). Everything is HTML-escaped first."""
    out, in_ul, in_ol = [], False, False

    def close():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
        if in_ol:
            out.append("</ol>")
        in_ul = in_ol = False

    for line in html.escape(text or "").splitlines():
        s = line.strip()
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        if not s:
            close()
        elif s.startswith("#"):
            close()
            out.append(f"<h3>{s.lstrip('#').strip()}</h3>")
        elif re.match(r"^[-*\u2022]\s+", s):
            if not in_ul:
                close()
                out.append("<ul>")
                in_ul = True
            out.append("<li>" + re.sub(r"^[-*\u2022]\s+", "", s) + "</li>")
        elif re.match(r"^\d+[.)]\s+", s):
            if not in_ol:
                close()
                out.append("<ol>")
                in_ol = True
            out.append("<li>" + re.sub(r"^\d+[.)]\s+", "", s) + "</li>")
        else:
            close()
            out.append(f"<p>{s}</p>")
    close()
    return "\n".join(out)


def build_offline_pack(farm: dict, today: datetime.date = None) -> str:
    today = today or datetime.date.today()
    e = html.escape
    prof = farm.get("profile", {})
    parts = [f"<h1>AgroNova offline pack</h1><p class='muted'>Saved on {today.isoformat()}. "
             f"{e(prof.get('name') or 'My farm')}, {e(prof.get('region') or '')} {e(prof.get('country') or '')}</p>",
             "<div class='card warn'>General guidance only. Confirm important decisions with your local agricultural officer. "
             "Forecasts and prices below were true when this file was saved.</div>"]

    fc = farm.get("weather")
    if fc and fc.get("daily"):
        days = "".join(f"<span class='day'><b>{e(d['date'][5:])}</b><br>{e(weather.describe_code(d['code'])[0])}<br>"
                       f"{d['tmin']:.0f}-{d['tmax']:.0f} C, rain {d['rain_mm']:.0f} mm</span>" for d in fc["daily"])
        parts.append(f"<h2>Forecast (saved {e(str(fc.get('fetched_at', '')))})</h2><section>{days}</section>")
        parts.append("<p class='muted'>" + e(weather.ATTRIBUTION) + "</p>")

    pending = [t for t in farm.get("tasks", []) if not t.get("done")]
    if pending:
        rows = "".join(f"<li><b>{e(str(t.get('due', '')))}</b> - {e(t.get('crop', ''))}: {e(t.get('title', ''))}</li>"
                       for t in sorted(pending, key=lambda t: str(t.get("due"))))
        parts.append(f"<h2>Upcoming tasks</h2><section><ul>{rows}</ul></section>")

    advice = farm.get("advice", [])
    if advice:
        parts.append("<h2>My saved advice</h2>")
        for a in advice:
            parts.append(f"<section><b>{e(a.get('title', ''))}</b><div class='muted'>{e(a.get('time', ''))} - "
                         f"{e(a.get('language', ''))}</div>{md_to_html(a.get('text', ''))}</section>")

    parts.append("<h2>Key guides</h2>")
    for g in GUIDES.values():
        items = "".join(f"<li>{e(s)}</li>" for s in g["steps"])
        parts.append(f"<section><b>{e(g['title'])}</b><ul>{items}</ul></section>")
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>AgroNova offline pack</title>"
            f"<style>{CSS}</style></head><body><main>{''.join(parts)}</main></body></html>")
