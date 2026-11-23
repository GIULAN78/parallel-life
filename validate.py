"""Validate Parallel Life data files. Usage: python3 validate.py [file ...]"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
MAX_EFFECT = 30
MAX_TEXT = 200
ALLOWED = {
    "id", "min_age", "max_age", "min_year", "max_year", "once", "max_times",
    "weight", "requires", "excludes", "text", "effects", "tags",
    "set_lifestyle", "health_risk",
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def check_event(event, label, stats, lifestyle, tags):
    problems = []

    def bad(message):
        problems.append(f"{label}: {message}")

    if not isinstance(event, dict):
        return [f"{label}: not an object"]
    label = f"{label} [{event.get('id', '?')}]"
    for key in ("id", "min_age", "max_age", "text"):
        if key not in event:
            bad(f"missing '{key}'")
    if problems:
        return problems
    for key in event:
        if key not in ALLOWED:
            bad(f"unknown field '{key}'")
    if not isinstance(event["id"], str) or not event["id"].strip():
        bad("id must be a non-empty string")
    if not is_int(event["min_age"]) or not is_int(event["max_age"]):
        bad("min_age and max_age must be integers")
    elif event["min_age"] > event["max_age"]:
        bad("min_age is greater than max_age")
    if "min_year" in event and "max_year" in event:
        if is_int(event["min_year"]) and is_int(event["max_year"]) and event["min_year"] > event["max_year"]:
            bad("min_year is greater than max_year")
    if not isinstance(event["text"], str) or not event["text"].strip():
        bad("text must be a non-empty string")
    elif len(event["text"]) > MAX_TEXT:
        bad(f"text is longer than {MAX_TEXT} characters")
    if "weight" in event and (not is_number(event["weight"]) or event["weight"] <= 0):
        bad("weight must be a positive number")
    if "max_times" in event and (not is_int(event["max_times"]) or event["max_times"] < 1):
        bad("max_times must be an integer >= 1")
    for flag in ("once", "health_risk"):
        if flag in event and not isinstance(event[flag], bool):
            bad(f"{flag} must be true or false")
    effects = event.get("effects", {})
    if not isinstance(effects, dict):
        bad("effects must be an object")
    else:
        for key, value in effects.items():
            if key not in stats:
                bad(f"effects: unknown variable '{key}'")
            elif not is_number(value) or abs(value) > MAX_EFFECT:
                bad(f"effects: '{key}' must be a number between -{MAX_EFFECT} and {MAX_EFFECT}")
    for field in ("requires", "excludes", "tags"):
        values = event.get(field, [])
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            bad(f"{field} must be a list of strings")
        elif field != "tags":
            for tag in values:
                if tag not in tags:
                    bad(f"{field}: unknown tag '{tag}'")
    changes = event.get("set_lifestyle", {})
    if not isinstance(changes, dict):
        bad("set_lifestyle must be an object")
    else:
        for key, value in changes.items():
            if key not in lifestyle:
                bad(f"set_lifestyle: unknown habit '{key}'")
            elif value not in [o["value"] for o in lifestyle[key]["options"]]:
                bad(f"set_lifestyle: unknown value '{value}' for '{key}'")
    return problems


def check_turning_point(tp, stats):
    problems = []
    label = f"turning_points.json [{tp.get('id', '?')}]"
    for key in ("id", "age", "label"):
        if key not in tp:
            problems.append(f"{label}: missing '{key}'")
    for key in tp.get("effects", {}):
        if key not in stats:
            problems.append(f"{label}: effects: unknown variable '{key}'")
    return problems


def check_themes(themes):
    problems = []
    entries = [("default", themes.get("default", {}))]
    entries += [(f"era {e.get('name', '?')}", e) for e in themes.get("eras", [])]
    entries += [(f"city {k}", v) for k, v in themes.get("cities", {}).items()]
    for name, entry in entries:
        for key in ("background", "surface", "accent", "text"):
            if key in entry and not HEX.match(str(entry[key])):
                problems.append(f"themes.json [{name}]: '{key}' is not a color like #1a2b3c")
    for era in themes.get("eras", []):
        if era.get("min_year", 0) > era.get("max_year", 0):
            problems.append(f"themes.json [{era.get('name', '?')}]: min_year is greater than max_year")
    return problems


def main():
    selected = {Path(a).resolve() for a in sys.argv[1:]}
    stats = {v["id"] for v in load(DATA / "core_variables.json")}
    lifestyle = load(DATA / "lifestyle.json")
    turning_points = load(DATA / "turning_points.json")
    event_paths = [DATA / "events.json"]
    event_paths += sorted((DATA / "packs").glob("*.json"))
    event_paths += sorted((DATA / "cities").glob("*.json"))

    problems = {}
    files = {}
    for path in event_paths:
        name = str(path.relative_to(ROOT))
        problems[name] = []
        try:
            data = load(path)
        except (json.JSONDecodeError, OSError) as error:
            problems[name].append(f"{name}: cannot read JSON ({error})")
            continue
        if not isinstance(data, list):
            problems[name].append(f"{name}: must contain a list of events")
            continue
        files[name] = data

    tags = set()
    for key, section in lifestyle.items():
        tags.update(f"{key}_{o['value']}" for o in section["options"])
    for tp in turning_points:
        tags.update(tp.get("tags", []))
    for data in files.values():
        for event in data:
            if isinstance(event, dict):
                tags.update(t for t in event.get("tags", []) if isinstance(t, str))

    seen = {}
    count = 0
    for name, data in files.items():
        for event in data:
            count += 1
            problems[name] += check_event(event, name, stats, lifestyle, tags)
            if isinstance(event, dict) and "id" in event:
                if event["id"] in seen:
                    problems[name].append(f"{name} [{event['id']}]: id already used in {seen[event['id']]}")
                seen[event["id"]] = name
    others = []
    for tp in turning_points:
        others += check_turning_point(tp, stats)
    others += check_themes(load(DATA / "themes.json"))

    total = 0
    for name, items in problems.items():
        if selected and (ROOT / name).resolve() not in selected:
            continue
        for item in items:
            print("ERROR", item)
            total += 1
    if not selected:
        for item in others:
            print("ERROR", item)
            total += 1
    if total:
        print(f"\n{total} problem(s) found.")
        sys.exit(1)
    print(f"OK: {count} events in {len(files)} files, no problems.")


if __name__ == "__main__":
    main()
