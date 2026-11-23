"""Parallel Life - simulation engine."""
import json
import random
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATS = ["health", "money", "happiness", "relationships", "career"]


def load_json(name):
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def default_stats():
    stats = {s: 50.0 for s in STATS}
    stats["health"] = 70.0
    return stats


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
