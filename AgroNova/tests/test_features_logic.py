"""Unit tests for the pure-Python feature modules (weather, calendar, store, market, sources, voice, offline, units, prompts).
No Streamlit and no network are needed.   Run:  python -m unittest discover -s tests -v
"""
import datetime
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import farmcal, market, offline, prompts, sources, store, units, voice, weather  # noqa: E402

RAW = {"timezone": "Asia/Kolkata",
       "current": {"temperature_2m": 31.2, "relative_humidity_2m": 60, "precipitation": 0.0, "weather_code": 2, "wind_speed_10m": 9.4},
       "daily": {"time": ["2026-11-04", "2026-11-05", "2026-11-06"], "weather_code": [2, 63, 95],
                 "temperature_2m_max": [33, 30, 29], "temperature_2m_min": [24, 23, 22],
                 "precipitation_sum": [0.0, 8.2, 25.0], "precipitation_probability_max": [10, 80, None],
                 "wind_speed_10m_max": [12, 18, 30]}}


def day(**kw):
    base = {"date": "2026-11-04", "code": 1, "tmax": 30, "tmin": 22, "rain_mm": 0.0, "rain_prob": 0.0, "wind_max": 8}
    base.update(kw)
    return base


class WeatherTests(unittest.TestCase):
    def test_normalize_handles_missing_probability(self):
        n = weather.normalize_forecast(RAW)
        self.assertEqual(len(n["daily"]), 3)
        self.assertEqual(n["daily"][2]["rain_prob"], 0.0)
        self.assertEqual(n["current"]["temp"], 31.2)

    def test_bad_response_is_a_friendly_error(self):
        with self.assertRaises(weather.WeatherError):
            weather.normalize_forecast({"nope": 1})

    def test_geocode_parsing(self):
        raw = {"results": [{"name": "Madurai", "admin1": "Tamil Nadu", "country": "India", "latitude": 9.9, "longitude": 78.1, "timezone": "Asia/Kolkata"},
                           {"name": "broken"}]}
        out = weather.parse_geocode(raw)
        self.assertEqual(len(out), 1)
        self.assertEqual(weather.place_label(out[0]), "Madurai, Tamil Nadu, India")
        self.assertEqual(weather.parse_geocode({}), [])

    def test_alerts_rain_hold_irrigation_and_no_spray(self):
        titles = [a["title"] for a in weather.farm_alerts([day(rain_mm=10, rain_prob=90), day(), day()])]
        self.assertIn("Hold irrigation for now", titles)
        self.assertIn("Avoid spraying today", titles)

    def test_alerts_hot_dry_and_good_spray(self):
        alerts = weather.farm_alerts([day(tmax=35), day(tmax=36), day(tmax=34)])
        titles = [a["title"] for a in alerts]
        self.assertIn("Hot and dry: plan watering", titles)
        self.assertIn("Good window for spraying", titles)
        self.assertIn("Dry spell: good for harvest and drying", titles)

    def test_alerts_storm_heat_frost(self):
        titles = [a["title"] for a in weather.farm_alerts([day(code=95, rain_mm=25), day(tmax=39), day(tmin=1)])]
        for t in ("Thunderstorm possible", "Heavy rain expected", "Heat stress risk", "Frost risk"):
            self.assertIn(t, titles)
        self.assertNotIn("Dry spell: good for harvest and drying", titles)

    def test_prompt_text_has_numbers_and_source(self):
        text = weather.forecast_for_prompt(weather.normalize_forecast(RAW), "Madurai")
        self.assertIn("LIVE FORECAST", text)
        self.assertIn("Madurai", text)
        self.assertIn("2026-11-05: Rain", text)

    def test_age_minutes(self):
        fc = {"fetched_at": "2026-11-04T10:00"}
        self.assertEqual(weather.age_minutes(fc, datetime.datetime(2026, 11, 4, 10, 45)), 45)
        self.assertEqual(weather.age_minutes({}), float("inf"))


class UnitsTests(unittest.TestCase):
    def test_conversion_only_changes_display(self):
        imp = "Imperial (acre, lb, °F, inch)"
        self.assertEqual(units.temp(0, imp), "32°F")
        self.assertEqual(units.temp(30, units.DEFAULT_UNITS), "30°C")
        self.assertEqual(units.rain(25.4, imp), "1.00 in")
        self.assertEqual(units.wind(100, imp), "62 mph")
        self.assertEqual(units.area_label("India (acre, quintal, °C, mm)"), "acre")
        self.assertIn("quintals", units.prompt_rule("India (acre, quintal, °C, mm)"))
        self.assertEqual(units.system("unknown")["short"], "Metric")


class CalendarTests(unittest.TestCase):
    def test_schedule_scales_with_maturity_and_matches_aliases(self):
        start = datetime.date(2026, 11, 1)
        t = farmcal.build_schedule("Paddy", start, 100)
        self.assertEqual(t[0]["kind"], "plant")
        self.assertEqual(t[-1]["kind"], "harvest")
        self.assertEqual(t[-1]["due"], (start + datetime.timedelta(days=100)).isoformat())
        self.assertEqual(farmcal.match_template("kambu")["label"].split()[0], "Pearl")
        self.assertEqual(farmcal.match_template("dragonfruit")["label"], "Generic crop")
        self.assertTrue(all("kg" not in x["title"] and " ml" not in x["title"] for x in t))   # no doses

    def test_stage_and_progress(self):
        self.assertEqual(farmcal.stage_for(-0.1), "Not planted yet")
        self.assertEqual(farmcal.stage_for(0.5), "Flowering / fruit set")
        self.assertEqual(farmcal.stage_for(1.5), "Past the expected harvest date")
        prog = farmcal.crop_progress({"name": "Rice", "planted": "2026-09-01"}, datetime.date(2026, 11, 4))
        self.assertEqual(prog["maturity"], 120)
        self.assertEqual(prog["days_to_harvest"], 120 - 64)
        self.assertEqual(farmcal.crop_progress({"name": "Rice"}, datetime.date.today())["stage"], "Planting date not set")

    def test_categorize(self):
        today = datetime.date(2026, 11, 10)
        mk = lambda d, done=False: {"id": d, "due": d, "done": done}
        g = farmcal.categorize([mk("2026-11-09"), mk("2026-11-10"), mk("2026-11-14"), mk("2026-12-30"), mk("2026-11-01", True)], today)
        self.assertEqual({k: len(v) for k, v in g.items()}, {"overdue": 1, "today": 1, "week": 1, "later": 1, "done": 1})

    def test_ai_tasks_are_validated(self):
        start = datetime.date(2026, 11, 1)
        out = farmcal.tasks_from_ai([{"day": 3, "kind": "water", "title": "Water"}, {"day": "x", "title": "bad"},
                                     {"day": 999, "title": "too far"}, {"day": 2, "kind": "magic", "title": "Odd kind"}, "junk"], "Rice", start)
        self.assertEqual([t["title"] for t in out], ["Odd kind", "Water"])
        self.assertEqual(out[0]["kind"], "other")
        self.assertEqual(farmcal.tasks_from_ai("not a list", "Rice", start), [])

    def test_ics_is_valid_and_escaped(self):
        tasks = farmcal.build_schedule("Rice", datetime.date(2026, 11, 1))
        tasks[0]["title"] = "Water; then, check\nfield " + "x" * 120
        tasks[1]["done"] = True
        ics = farmcal.make_ics(tasks, "Selvi's farm, TN", now=datetime.datetime(2026, 11, 4, 6, 0, 0))
        self.assertTrue(ics.startswith("BEGIN:VCALENDAR\r\n") and ics.endswith("END:VCALENDAR\r\n"))
        self.assertEqual(ics.count("BEGIN:VEVENT"), len(tasks) - 1)       # finished tasks are skipped
        self.assertEqual(ics.count("BEGIN:VEVENT"), ics.count("END:VEVENT"))
        self.assertIn("DTSTART;VALUE=DATE:20261101", ics)
        self.assertIn("\\;", ics)
        self.assertTrue(all(len(line.encode("utf-8")) <= 75 for line in ics.split("\r\n")))


class StoreTests(unittest.TestCase):
    def test_round_trip_and_cleaning(self):
        farm = store.new_farm()
        farm["profile"]["region"] = "Tamil Nadu"
        farm["profile"]["crops"] = [{"name": "Rice"}, {"name": "  "}, "junk"]
        store.add_advice(farm, "crop", "Title", "text", "Tamil", [{"url": "https://x"}])
        loaded = store.from_json(store.to_json(farm).replace('"crops"', '"crops"'))
        self.assertEqual(loaded["profile"]["region"], "Tamil Nadu")
        self.assertEqual(loaded["advice"][0]["title"], "Title")
        self.assertEqual(loaded["profile"]["crops"], [{"name": "Rice"}])

    def test_bad_files_are_rejected(self):
        for bad in ("", "not json", "[]", '{"x": 1}'):
            with self.assertRaises(ValueError):
                store.from_json(bad)

    def test_unknown_keys_are_dropped_and_caps_applied(self):
        data = {"profile": {"region": "R", "evil": "<script>"}, "advice": [{"id": str(i)} for i in range(100)], "hacker": 1}
        farm = store.from_json(json.dumps(data))
        self.assertNotIn("evil", farm["profile"])
        self.assertNotIn("hacker", farm)
        self.assertEqual(len(farm["advice"]), store.MAX_ADVICE)

    def test_photos_are_shrunk_and_bad_images_rejected(self):
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (3000, 2000), (20, 140, 60)).save(buf, "PNG")
        raw, mime = store.prepare_image(buf.getvalue(), max_px=800)
        self.assertEqual(mime, "image/jpeg")
        self.assertEqual(max(Image.open(io.BytesIO(raw)).size), 800)
        self.assertLess(len(store.make_thumbnail(buf.getvalue())), 20000)
        with self.assertRaises(ValueError):
            store.prepare_image(b"definitely not an image")

    def test_local_save_and_load(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "sub" / "farm.json"
            farm = store.new_farm()
            farm["profile"]["name"] = "Selvi"
            self.assertTrue(store.save_local(farm, path))
            self.assertEqual(store.load_local(path)["profile"]["name"], "Selvi")
            self.assertIsNone(store.load_local(Path(d) / "missing.json"))

    def test_journal_helpers(self):
        farm = store.new_farm()
        store.add_journal(farm, {"kind": "Harvest", "crop": "Rice", "qty": 120, "qty_unit": "kg"})
        store.add_journal(farm, {"kind": "Harvest", "crop": "Rice", "qty": "30", "qty_unit": "kg"})
        store.add_journal(farm, {"kind": "Watering", "crop": "Rice", "qty": 5})
        store.add_journal(farm, {"kind": "Harvest", "crop": "Maize", "qty": "oops"})
        self.assertEqual(store.harvest_totals(farm["journal"]), {"Rice": {"kg": 150.0}})
        store.delete_by_id(farm["journal"], farm["journal"][0]["id"])
        self.assertEqual(len(farm["journal"]), 3)


class MarketTests(unittest.TestCase):
    RAW = {"records": [{"state": "Tamil Nadu", "market": "A", "commodity": "Tomato", "min_price": "1800", "max_price": "2600", "modal_price": "2200"},
                       {"state": "Tamil Nadu", "market": "B", "commodity": "Tomato", "min_price": "1500", "max_price": "2400", "modal_price": "2000"},
                       {"commodity": "Empty"}, "junk"]}

    def test_parse_and_summarize(self):
        rows = market.parse_agmarknet(self.RAW)
        self.assertEqual(len(rows), 2)
        s = market.summarize(rows)[0]
        self.assertEqual((s["commodity"], s["markets"], s["avg_modal"], s["lowest"], s["highest"]), ("Tomato", 2, 2100.0, 1500.0, 2600.0))
        self.assertEqual(market.parse_agmarknet({}), [])

    def test_no_key_is_friendly(self):
        with self.assertRaises(market.MarketError):
            market.fetch_agmarknet("")

    def test_margin_uses_only_given_numbers(self):
        out = market.margin_table([{"crop": "Tomato", "price": 20, "yield_per_area": 8000, "cost_per_area": 90000},
                                   {"crop": "Paddy", "price": 22, "yield_per_area": 2500, "cost_per_area": 30000},
                                   {"crop": "Incomplete", "price": 5}, {"crop": "", "price": 1, "yield_per_area": 1, "cost_per_area": 1},
                                   {"crop": "Negative", "price": -1, "yield_per_area": 1, "cost_per_area": 1}])
        self.assertEqual([r["crop"] for r in out], ["Tomato", "Paddy"])
        self.assertEqual(out[0]["margin"], 70000)


class SourcesVoiceOfflineTests(unittest.TestCase):
    def test_sources_are_https_unique_and_local_first(self):
        links = sources.links_for("India", "Tamil Nadu", "doctor")
        self.assertTrue(all(l["url"].startswith("https://") for l in links))
        self.assertEqual(len({l["url"] for l in links}), len(links))
        self.assertIn("icar.org.in", links[0]["url"])
        self.assertTrue(any("tnau" in l["url"] for l in links))
        self.assertTrue(sources.links_for("Atlantis", "", "crop"))   # always at least the global link

    def test_voice_text_and_player(self):
        self.assertEqual(voice.strip_markdown("## Overview\n- **Plant** rice [link](http://x)\n1. Water"), "Overview.\nPlant rice link\nWater")
        self.assertEqual(voice.lang_code("Tamil"), "ta-IN")
        page = voice.speak_html("Hello </script><b>x</b>", "Hindi")
        self.assertNotIn("</script><b>", page)
        self.assertIn("hi-IN", page)

    def test_offline_pack_escapes_everything(self):
        farm = store.new_farm()
        farm["profile"]["name"] = "<img src=x onerror=alert(1)>"
        store.add_advice(farm, "crop", "<script>x</script>", "## Overview\n- **Rice** <b>bold</b>\n", "English")
        farm["tasks"] = [{"id": "a", "crop": "Rice", "title": "<i>Weed</i>", "due": "2026-11-10", "done": False}]
        farm["weather"] = weather.normalize_forecast(RAW)
        html_doc = offline.build_offline_pack(farm, datetime.date(2026, 11, 4))
        for raw in ("<script>x", "<img src=x", "<i>Weed", "<b>bold"):
            self.assertNotIn(raw, html_doc)
        self.assertIn("Key guides", html_doc)
        self.assertIn("Open-Meteo", html_doc)
        self.assertNotIn("http://", html_doc.replace("http://www.w3.org", ""))   # nothing is fetched: fully self-contained


class PromptV2Tests(unittest.TestCase):
    def test_detail_units_and_extra_reach_the_prompt(self):
        p = prompts.build_prompt_v2("forecast", {"Region": "TN"}, "Tamil", "Short and simple", units.prompt_rule(units.DEFAULT_UNITS), "LIVE FORECAST x")
        self.assertIn("under about 180 words", p)
        self.assertNotIn("450 words", p)
        self.assertIn("metric units", p.lower())
        self.assertIn("LIVE FORECAST x", p)
        self.assertIn("Write the answer in Tamil", p)
        for t in prompts.SECTION_TITLES:
            self.assertIn(f"## {t}", p)
        self.assertIn("up to about 800 words", prompts.build_prompt_v2("ask", {}, "English", "Detailed"))

    def test_system_rules_cover_photos_and_forecast(self):
        self.assertIn("LIVE FORECAST", prompts.SYSTEM_INSTRUCTION)
        self.assertIn("NEVER invent weather", prompts.SYSTEM_INSTRUCTION)
        self.assertIn("photo", prompts.SYSTEM_INSTRUCTION.lower())

    def test_question_parsing_survives_bad_model_output(self):
        good = [{"question": "Where did it start?", "options": ["Bottom leaves", "Top leaves", "Not sure"]}]
        self.assertEqual(prompts.parse_questions(good), good)
        self.assertEqual(prompts.parse_questions({"questions": good}), good)
        self.assertEqual(prompts.parse_questions([{"question": "", "options": []}, {"question": "x", "options": ["only one"]}, 5]), [])
        self.assertEqual(prompts.parse_questions("garbage"), [])
        self.assertEqual(len(prompts.parse_questions(good * 9)), 5)
        self.assertIn("A photo of the plant is attached", prompts.build_question_prompt("tomato", "TN", "spots", "Leaves", "Tamil", True))


if __name__ == "__main__":
    unittest.main()
