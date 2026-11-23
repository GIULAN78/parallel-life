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


@dataclass
class Avatar:
    name: str
    birth_year: int
    city: str
    stats: dict = field(default_factory=lambda: {s: 50 for s in STATS})
    tags: set = field(default_factory=set)
    counts: dict = field(default_factory=dict)
    timeline: list = field(default_factory=list)


def apply_effects(avatar, effects):
    for key, value in effects.items():
        if key in avatar.stats:
            avatar.stats[key] = max(0, min(100, avatar.stats[key] + value))


def apply_turning_point(avatar, turning_point):
    apply_effects(avatar, turning_point.get("effects", {}))
    avatar.tags.update(turning_point.get("tags", []))


def is_eligible(event, age, avatar):
    if not event["min_age"] <= age <= event["max_age"]:
        return False
    max_times = 1 if event.get("once", False) else event.get("max_times", 1000)
    if avatar.counts.get(event["id"], 0) >= max_times:
        return False
    if not set(event.get("requires", [])) <= avatar.tags:
        return False
    if set(event.get("excludes", [])) & avatar.tags:
        return False
    return True


def simulate(avatar, events, start_age, end_age, seed=None):
    rng = random.Random(seed)
    for age in range(start_age, end_age + 1):
        avatar.stats["health"] = max(0, avatar.stats["health"] - (1 if age > 50 else 0))
        pool = [e for e in events if is_eligible(e, age, avatar)]
        if not pool or rng.random() > 0.7:
            continue
        event = rng.choices(pool, weights=[e.get("weight", 1) for e in pool], k=1)[0]
        apply_effects(avatar, event.get("effects", {}))
        avatar.tags.update(event.get("tags", []))
        avatar.counts[event["id"]] = avatar.counts.get(event["id"], 0) + 1
        avatar.timeline.append((avatar.birth_year + age, age, event["text"]))
    return avatar
