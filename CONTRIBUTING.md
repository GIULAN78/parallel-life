# Contributing to Parallel Life

Everyone can add their own piece. Most contributions need no programming: events, turning points and lifestyle options are plain JSON files in the `data/` folder.

## Add an event (`data/events.json`)

Each event is one line:

    {"id": "gallery", "min_age": 22, "max_age": 60, "once": true, "weight": 3,
     "requires": ["artist"], "text": "A local gallery exhibits your work.",
     "effects": {"happiness": 12, "career": 6}}

Fields:

- `id`: unique name of the event.
- `min_age`, `max_age`: ages between which the event can happen.
- `weight`: how likely it is compared to other eligible events.
- `once`: if true, it happens at most once. Alternatively use `max_times`.
- `requires`: tags the avatar must have (turning points and events add tags).
- `excludes`: tags that prevent the event.
- `text`: what the player reads.
- `effects`: changes to stats (`health`, `money`, `happiness`, `relationships`, `career`).
- `tags`: tags the event adds to the avatar.
- `set_lifestyle`: changes a lifestyle habit, for example `{"smoking": "former"}`.
- `health_risk`: if true, an unhealthy lifestyle makes the event more likely.

Lifestyle values are available as tags in the form `key_value`, for example `smoking_smoker` or `activity_low`.

## Add a turning point (`data/turning_points.json`)

A turning point is the choice that starts the parallel life: `id`, `age`, `label`, `effects` and `tags`.

## Tune the model (`data/config.json`, `data/lifestyle.json`)

Aging, event frequency and the health effect of each habit are plain numbers. Changing them lets you simulate other scenarios, such as longer lives in the future.

## Run and test

    python3 main.py

## Rules

- Keep texts short and neutral.
- Do not include real people or private data.
- Open an issue before large changes.

## Add your city (`data/cities/`)

Create a file named after your city in lowercase, with dashes instead of spaces and no accents (for example `data/cities/grignasco.json`). It contains a list of events in the same format as above. When a player types that city, its events are added to the general ones. Keep them true to the place and respectful of its people.
