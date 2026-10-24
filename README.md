# second-brain

## Installation

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd second-brain
   ```

2. Install dependencies (this creates `.venv` and installs the package with dev tools):

   ```bash
   uv sync
   ```

## Usage

Run via the CLI entrypoint:

```bash
uv run second_brain
```

Run with the development environment:

```bash
uv run --env-file .env second_brain
```

Run as a Python module:

```bash
uv run python -m second_brain
```

## Environment Variables

`.env.example` is the committed template. Copy it to `.env` for development:

```bash
cp .env.example .env
```

| Variable    | Default   | Description                                                        |
|-------------|-----------|--------------------------------------------------------------------|
| `LOG_LEVEL` | `INFO`    | Console log level. Set to `DEBUG` in `.env` for verbose output.    |
| `LOG_FILE`  | `app.log` | Path to the log file (always written at `DEBUG` level).            |

Environment files are not loaded automatically. Use `uv run --env-file .env` to load
the dev environment explicitly.

## Logging

Console (stderr) and `LOG_FILE` use the same format, with no milliseconds and a
three-letter level shorthand:

```text
2026-10-24 20:33:18 | INF | second_brain.app:main:29 - Hello from second_brain!
```

| Level      | Shorthand |
|------------|-----------|
| `TRACE`    | `TRC`     |
| `DEBUG`    | `DBG`     |
| `INFO`     | `INF`     |
| `SUCCESS`  | `SUC`     |
| `WARNING`  | `WRN`     |
| `ERROR`    | `ERR`     |
| `CRITICAL` | `CRT`     |

Custom levels keep their full name. Console output is colored by level when
attached to a terminal; the log file is plain text.

## Testing

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov
```

## Documentation

Preview the docs locally (output is also written to `mkdocs.log`):

```bash
uv run python scripts/serve_docs.py
```

Build the static site:

```bash
uv run mkdocs build
```
