# Architecture

Three views of the `second_brain` package: how its files and functions fit
together, how it is launched, and what a typical session looks like.

## Package overview

Every module in `src/second_brain/`, grouped into components, with the
functions each one defines and how they import and call each other.

```mermaid
---
title: second_brain — files, functions and imports
---
flowchart LR
    subgraph entry["Entry points"]
        direction TB
        console_script["pyproject.toml<br/>[project.scripts]<br/>second_brain"]
        main_module["__main__.py"]
        init_module["__init__.py<br/>(empty package marker)"]
    end

    subgraph cli_mod["CLI layer — cli.py · imports click, loguru"]
        direction TB
        cli_group["cli()<br/>@click.group"]
        cmd_new["new()"]
        cmd_list["list_notes()<br/>command name: list"]
        cmd_show["show()"]
    end

    subgraph app_mod["Logging — app.py · imports sys, os, loguru"]
        direction LR
        fn_app_main["main()<br/>@logger.catch<br/>(no entry point calls it)"]
        fn_configure["configure_logging()<br/>reads LOG_LEVEL, LOG_FILE"]
        fn_stderr_format["stderr_format()"]
        const_levels["LEVEL_SHORT_NAMES"]
    end

    subgraph notes_mod["Notes domain — notes.py · imports os, re, unicodedata, datetime, pathlib"]
        direction TB
        fn_notes_dir["notes_dir()<br/>reads SECOND_BRAIN_DIR"]
        fn_list_files["list_note_files()"]
        fn_read_note["read_note()"]
        fn_create_note["create_note()"]
        fn_split["split_title_body()"]
        fn_clean["_clean_block()"]
        fn_build_path["build_note_path()"]
        fn_slugify["slugify()"]
    end

    log_sinks[("stderr · app.log")]
    notes_store[("notes directory<br/>YYYY-MM-DD-slug.md")]

    console_script ==> cli_group
    main_module ==> cli_group

    cli_group --> cmd_new & cmd_list & cmd_show
    cli_group ==> fn_configure
    cmd_show ==> fn_notes_dir & fn_list_files & fn_read_note
    cmd_list ==> fn_notes_dir & fn_list_files
    cmd_new ==> fn_notes_dir & fn_create_note

    fn_app_main --> fn_configure --> fn_stderr_format --> const_levels
    fn_create_note --> fn_split --> fn_clean
    fn_create_note --> fn_build_path --> fn_slugify

    fn_configure -.->|writes| log_sinks
    fn_list_files -.->|glob| notes_store
    fn_read_note -.->|read| notes_store
    fn_create_note -.->|write| notes_store
```

| Line style | Meaning |
|------------|---------|
| `==>` thick | Cross-module import, then a call (`from second_brain.x import y`) |
| `-->` solid | Call within the same module, or a Click subcommand of the group |
| `-.->` dotted | File I/O: log output and the notes directory |

| Module | Imports from the package | Third-party | Tested by |
|--------|--------------------------|-------------|-----------|
| `__main__.py` | `cli.cli` | — | — (excluded from coverage) |
| `cli.py` | `app.configure_logging`, `notes.create_note`, `notes.list_note_files`, `notes.notes_dir`, `notes.read_note` | `click`, `loguru` | `tests/test_cli.py` |
| `notes.py` | — | — | `tests/test_notes.py` |
| `app.py` | — | `loguru` | `tests/test_app.py` |

`notes.py` and `app.py` never import each other, and neither imports `cli.py`,
so dependencies only point from the CLI layer inwards.

## Entry points and arguments

The ways to start the program, the arguments each command takes, and the steps
and exit paths behind every command.

```mermaid
---
title: second_brain — entry points, arguments and what runs behind them
---
flowchart LR
    subgraph launch["Ways to launch"]
        direction TB
        run_uv["uv run --env-file .env second_brain …"]
        run_script["second_brain …<br/>console script"]
        run_module["python -m second_brain …"]
        main_py["__main__.py"]
        app_main["app.main()<br/>not wired to any launcher"]
    end

    group["<b>cli</b> group<br/>--help on the group and every command"]
    setup_logs["configure_logging()<br/>reads LOG_LEVEL, LOG_FILE<br/>stderr at LOG_LEVEL · file at DEBUG"]

    run_uv --> run_script
    run_script --> group
    run_module --> main_py --> group
    group -->|"always, before the command"| setup_logs

    group --> new_cmd
    group --> list_cmd
    group --> show_cmd

    subgraph new_flow["new"]
        direction LR
        new_cmd["<b>new</b> TITLE [--body TEXT]<br/>TITLE: required, may be multi-line<br/>--body / -b: optional body text<br/>--body -: read body from stdin"]
        new_stdin{"--body is '-'?"}
        new_read["read body from stdin"]
        new_dir["notes_dir()<br/>reads SECOND_BRAIN_DIR"]
        new_create["create_note()<br/>split_title_body → build_note_path → slugify<br/>never overwrites: appends -1, -2, …"]
        new_out[["stdout: absolute path of the note<br/>exit 0"]]
        new_cmd --> new_stdin
        new_stdin -->|yes| new_read --> new_dir
        new_stdin -->|no| new_dir
        new_dir --> new_create --> new_out
    end

    subgraph list_flow["list"]
        direction LR
        list_cmd["<b>list</b><br/>no arguments"]
        list_dir["notes_dir()<br/>reads SECOND_BRAIN_DIR"]
        list_exists{"directory exists?"}
        list_files["list_note_files()<br/>*.md, newest first"]
        list_any{"any notes?"}
        list_missing[["stdout: Notes directory does not exist<br/>exit 0"]]
        list_none[["stdout: Notes: dir · No notes found.<br/>exit 0"]]
        list_out[["stdout: Notes: dir<br/>1. newest.md · 2. …<br/>exit 0"]]
        list_cmd --> list_dir --> list_exists
        list_exists -->|no| list_missing
        list_exists -->|yes| list_files --> list_any
        list_any -->|no| list_none
        list_any -->|yes| list_out
    end

    subgraph show_flow["show"]
        direction LR
        show_cmd["<b>show</b> NUMBER<br/>NUMBER: required int<br/>position from list, 1 = newest"]
        show_dir["notes_dir()<br/>reads SECOND_BRAIN_DIR"]
        show_exists{"directory exists?"}
        show_files["list_note_files()"]
        show_any{"any notes?"}
        show_range{"1 ≤ NUMBER ≤ count?"}
        show_read["read_note()"]
        show_err[["stderr: Error: …<br/>exit 1"]]
        show_out[["stdout: note markdown<br/>exit 0"]]
        show_cmd --> show_dir --> show_exists
        show_exists -->|yes| show_files --> show_any
        show_any -->|yes| show_range
        show_range -->|yes| show_read --> show_out
        show_exists -->|no| show_err
        show_any -->|no| show_err
        show_range -->|no| show_err
    end
```

| Variable | Default | Read by |
|----------|---------|---------|
| `SECOND_BRAIN_DIR` | `~/second_brain/` | `notes_dir()`, on every call |
| `LOG_LEVEL` | `INFO` | `configure_logging()`, stderr sink only |
| `LOG_FILE` | `app.log` | `configure_logging()`, file sink always logs at `DEBUG` |

A missing `TITLE` or `NUMBER`, or a `NUMBER` that is not an integer, is
rejected by Click before any of these steps run (exit status 2).

## Example user flow

Capturing an idea, finding it again later and reading it back, including the
most common mistake: asking for a number that `list` did not show.

```mermaid
---
title: second_brain — capture, find and read a note
---
flowchart LR
    idea(["An idea pops up"])
    kind{"How much is there<br/>to write down?"}
    new_quick["second_brain new 'Caching idea'"]
    new_body["second_brain new 'Caching idea'<br/>--body 'Use an LRU. Check limits.'"]
    new_pipe["cat draft.md #124; second_brain new 'Draft' --body -"]
    saved[["stdout<br/>/home/you/second_brain/2026-10-25-caching-idea.md"]]
    note_file[("2026-10-25-caching-idea.md<br/>#35; Caching idea<br/>Use an LRU. Check limits.<br/>2026-10-25T09:30:00")]

    later(["Later: find it again"])
    list_cmd["second_brain list"]
    listing[["Notes: /home/you/second_brain<br/>1. 2026-10-25-draft.md<br/>2. 2026-10-25-caching-idea.md"]]
    show_cmd["second_brain show 2"]
    valid{"Number shown<br/>by list?"}
    content[["stdout: the note's markdown"]]
    reuse(["Read it, or pipe it on<br/>second_brain show 2 #124; less"])
    error[["stderr: Error: Note 9 not found.<br/>Only 2 notes available.<br/>exit 1"]]

    idea --> kind
    kind -->|"a title"| new_quick
    kind -->|"title and details"| new_body
    kind -->|"a draft file"| new_pipe
    new_quick & new_body & new_pipe --> saved --> note_file
    note_file --> later --> list_cmd --> listing --> show_cmd --> valid
    valid -->|yes| content --> reuse
    valid -->|"no, e.g. show 9"| error
    error -.->|"check the numbers again"| list_cmd
```
