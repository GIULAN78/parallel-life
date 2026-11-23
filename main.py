"""Parallel Life - text prototype. Run: python3 main.py"""
from parallel_life.engine import STATS, Avatar, apply_turning_point, load_json, simulate

DEFAULT_END_AGE = 100


def ask(prompt, default=None):
    value = input(prompt).strip()
    return value if value else default


def main():
    print("=== PARALLEL LIFE ===")
    print("Live the life you didn't choose.\n")
    name = ask("Avatar name: ", "Anonymous")
    birth_year = int(ask("Year of birth: ", "1990"))
    city = ask("Your city: ", "Unknown")
    avatar = Avatar(name=name, birth_year=birth_year, city=city)

    turning_points = load_json("turning_points.json")
    events = load_json("events.json")

    print("\nPick your turning point:")
    for i, tp in enumerate(turning_points, 1):
        print(f"  {i}. {tp['label']} (age {tp['age']})")
    choice = int(ask("Number: ", "1")) - 1
    tp = turning_points[choice]
    apply_turning_point(avatar, tp)

    end_age = int(ask(f"Simulate until age (default {DEFAULT_END_AGE}): ", str(DEFAULT_END_AGE)))
    simulate(avatar, events, tp["age"], end_age)

    print(f"\n--- The parallel life of {avatar.name} in {avatar.city} ---")
    print(f"{avatar.birth_year + tp['age']} (age {tp['age']}): {tp['label']}.")
    for year, age, text in avatar.timeline:
        print(f"{year} (age {age}): {text}")
    print("\nFinal stats:")
    for stat in STATS:
        print(f"  {stat:<14} {avatar.stats[stat]:>3}")


if __name__ == "__main__":
    main()
