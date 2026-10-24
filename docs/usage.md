# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

Via the CLI entrypoint:

```bash
uv run second_brain                          # production defaults
uv run --env-file .env second_brain          # dev settings
```

Or as a Python module:

```bash
uv run python -m second_brain
```

## Environment Variables

| Variable    | Default    | Description                          |
|-------------|------------|--------------------------------------|
| `LOG_LEVEL` | `INFO`     | Console log level (DEBUG, INFO, …)   |
| `LOG_FILE`  | `app.log`  | Path to the log file                 |

Copy `.env.example` to `.env` for development defaults, then run with `uv run --env-file .env`.

## Logging

Console (stderr) and the log file share the same format:

```text
2026-10-24 20:33:18 | INF | second_brain.app:main:29 - Hello from second_brain!
```

Timestamps have no milliseconds. Levels are shown as a three-letter shorthand:

| Level      | Shorthand |
|------------|-----------|
| `TRACE`    | `TRC`     |
| `DEBUG`    | `DBG`     |
| `INFO`     | `INF`     |
| `SUCCESS`  | `SUC`     |
| `WARNING`  | `WRN`     |
| `ERROR`    | `ERR`     |
| `CRITICAL` | `CRT`     |

Custom levels that are not in this table keep their full name (e.g. `NOTICE`).
Console output is colored by level when attached to a terminal; the log file is plain text.

The format is defined by `LOG_FORMAT` and the mapping by `LEVEL_SHORTHAND` in
`second_brain.app` (see the [API Reference](api.md)).
