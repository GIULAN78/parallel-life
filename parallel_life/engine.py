"""Parallel Life - simulation engine."""
import json
import random
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(name):
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


CORE_VARIABLES = load_json("core_variables.json")
STATS = [v["id"] for v in CORE_VARIABLES]


def city_slug(name):
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return "-".join(text.lower().split())


def load_city_events(city):
    path = DATA_DIR / "cities" / f"{city_slug(city)}.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_packs():
    events = []
    packs_dir = DATA_DIR / "packs"
    if packs_dir.exists():
        for path in sorted(packs_dir.glob("*.json")):
            with open(path, encoding="utf-8") as f:
                events.extend(json.load(f))
    return events


def get_theme(city, year):
    themes = load_json("themes.json")
    theme = dict(themes["default"])
    for era in themes.get("eras", []):
        if era["min_year"] <= year <= era["max_year"]:
            theme.update(era)
            break
    theme.update(themes.get("cities", {}).get(city_slug(city), {}))
    return theme


def default_stats():
    return {v["id"]: float(v["start"]) for v in CORE_VARIABLES}


@dataclass
class Avatar:
    name: str
    birth_year: int
    city: str
    stats: dict = field(default_factory=default_stats)
    tags: set = field(default_factory=set)
    lifestyle: dict = field(default_factory=dict)
    counts: dict = field(default_factory=dict)
    timeline: list = field(default_factory=list)


def clamp(value):
    return max(0.0, min(100.0, value))


def apply_effects(avatar, effects):
    for key, value in effects.items():
        if key in avatar.stats:
            avatar.stats[key] = clamp(avatar.stats[key] + value)


def apply_turning_point(avatar, turning_point):
    apply_effects(avatar, turning_point.get("effects", {}))
    avatar.tags.update(turning_point.get("tags", []))


def active_tags(avatar):
    tags = set(avatar.tags)
    for key, value in avatar.lifestyle.items():
        tags.add(f"{key}_{value}")
    return tags


def lifestyle_score(avatar, lifestyle):
    total = 0.0
    for key, section in lifestyle.items():
        chosen = avatar.lifestyle.get(key, section["default"])
        for option in section["options"]:
            if option["value"] == chosen:
                total += option["health"]
    return total


def is_eligible(event, age, avatar):
    if not event["min_age"] <= age <= event["max_age"]:
        return False
    year = avatar.birth_year + age
    if year < event.get("min_year", -10000) or year > event.get("max_year", 10000):
        return False
    max_times = 1 if event.get("once", False) else event.get("max_times", 1000)
    if avatar.counts.get(event["id"], 0) >= max_times:
        return False
    tags = active_tags(avatar)
    if not set(event.get("requires", [])) <= tags:
        return False
    if set(event.get("excludes", [])) & tags:
        return False
    return True


def simulate(avatar, events, start_age, end_age, config, lifestyle, seed=None):
    rng = random.Random(seed)
    for age in range(start_age, end_age + 1):
        score = lifestyle_score(avatar, lifestyle)
        avatar.stats["health"] = clamp(avatar.stats["health"] + score)
        if age > config["aging_start_age"]:
            avatar.stats["health"] = clamp(avatar.stats["health"] - config["aging_health_per_year"])
        pool = [e for e in events if is_eligible(e, age, avatar)]
        if not pool or rng.random() > config["event_chance"]:
            continue
        weights = []
        for e in pool:
            weight = e.get("weight", 1)
            if e.get("health_risk", False):
                weight *= max(0.3, 1 - 2 * score)
            weights.append(weight)
        event = rng.choices(pool, weights=weights, k=1)[0]
        apply_effects(avatar, event.get("effects", {}))
        avatar.tags.update(event.get("tags", []))
        avatar.lifestyle.update(event.get("set_lifestyle", {}))
        avatar.counts[event["id"]] = avatar.counts.get(event["id"], 0) + 1
        avatar.timeline.append((avatar.birth_year + age, age, event["text"]))
    return avatar
