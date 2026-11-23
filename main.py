"""Parallel Life - text prototype. Run: python3 main.py"""
from parallel_life.engine import (
    CORE_VARIABLES, Avatar, apply_turning_point, load_city_events, load_json, simulate,
)

DEFAULT_END_AGE = 100


def ask(prompt, default=None):
    value = input(prompt).strip()
    return value if value else default


def ask_lifestyle(lifestyle):
    chosen = {}
    print("\nYour lifestyle (Enter keeps the default):")
    for key, section in lifestyle.items():
        options = section["options"]
        print(f"\n{section['question']}:")
        default_index = 1
        for i, option in enumerate(options, 1):
            marker = ""
            if option["value"] == section["default"]:
                default_index = i
                marker = " (default)"
            print(f"  {i}. {option['label']}{marker}")
        index = int(ask("Number: ", str(default_index))) - 1
        chosen[key] = options[index]["value"]
    return chosen


def main():
    print("=== PARALLEL LIFE ===")
    print("Live the life you didn't choose.\n")
    name = ask("Avatar name: ", "Anonymous")
    birth_year = int(ask("Year of birth: ", "1990"))
    city = ask("Your city: ", "Unknown")
    avatar = Avatar(name=name, birth_year=birth_year, city=city)

    turning_points = load_json("turning_points.json")
    events = load_json("events.json")
    city_events = load_city_events(city)
    events = events + city_events
    config = load_json("config.json")
    lifestyle = load_json("lifestyle.json")

    if city_events:
        print(f"Local events loaded for {city}: {len(city_events)}")
    else:
        print(f"No local pack for {city} yet: only general events (anyone can add one).")

    avatar.lifestyle = ask_lifestyle(lifestyle)

    print("\nPick your turning point:")
    for i, tp in enumerate(turning_points, 1):
        print(f"  {i}. {tp['label']} (age {tp['age']})")
    choice = int(ask("Number: ", "1")) - 1
    tp = turning_points[choice]
    apply_turning_point(avatar, tp)

    end_age = int(ask(f"Simulate until age (default {DEFAULT_END_AGE}): ", str(DEFAULT_END_AGE)))
    simulate(avatar, events, tp["age"], end_age, config, lifestyle)

    print(f"\n--- The parallel life of {avatar.name} in {avatar.city} ---")
    print(f"{avatar.birth_year + tp['age']} (age {tp['age']}): {tp['label']}.")
    for year, age, text in avatar.timeline:
        print(f"{year} (age {age}): {text}")
    print("\nFinal stats:")
    current_group = None
    for var in CORE_VARIABLES:
        if var["group"] != current_group:
            current_group = var["group"]
            print(f"\n  [{current_group}]")
        print(f"    {var['label']:<16} {round(avatar.stats[var['id']]):>3}")


if __name__ == "__main__":
    main()
