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

## Eras: past, present and future

Any event can have `min_year` and `max_year`, so it only happens in that period. A person born in 1950 will see the events of their time. This lets anyone rebuild how a place used to be, or imagine how it could be.

- Events valid for a whole era, in any city, go in `data/packs/` (one file per pack, for example `past_1950_1980.json`).
- Events about one place go in `data/cities/<city>.json`, with years if they belong to a period.
- Historical packs must describe places, trades and customs, never real or private people.

## Colors and themes (`data/themes.json`)

The palette changes with the era and the place: a default theme, one theme per era (by year range) and optional overrides for a single city, for example a different accent color.
