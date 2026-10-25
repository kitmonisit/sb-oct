import io
import os
import re

import pytest
from loguru import logger

from second_brain.app import (
    configure_logging,
    log_dir,
    log_file_path,
    main,
    stderr_format,
)

STDERR_LINE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| INF \| "
    r"second_brain\.app:main:\d+ \| Hello from second_brain!$"
)


def test_main_logs_greeting(capfd):
    main()
    captured = capfd.readouterr()
    assert "Hello from second_brain!" in captured.err


def test_stderr_line_format(capfd):
    main()
    lines = capfd.readouterr().err.splitlines()
    assert any(STDERR_LINE.match(line) for line in lines), lines


@pytest.mark.parametrize(
    ("level", "short"),
    [
        ("TRACE", "TRC"),
        ("DEBUG", "DBG"),
        ("INFO", "INF"),
        ("SUCCESS", "SUC"),
        ("WARNING", "WRN"),
        ("ERROR", "ERR"),
        ("CRITICAL", "CRT"),
    ],
)
def test_level_short_names(capfd, monkeypatch, level, short):
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    configure_logging()
    logger.log(level, "level check")
    err = capfd.readouterr().err
    assert f" | {short} | " in err
    assert f" | {level}" not in err


def test_custom_level_falls_back_to_first_three_chars(capfd):
    logger.level("NOTICE_T", no=25)
    configure_logging()
    logger.log("NOTICE_T", "custom level")
    assert " | NOT | " in capfd.readouterr().err


@pytest.mark.parametrize("name", ["{<x", "<b>X", "{0}"])
def test_custom_level_with_markup_chars_does_not_crash(capfd, name):
    logger.level(name, no=26)
    configure_logging()
    logger.log(name, "odd level")
    err = capfd.readouterr().err
    assert f" | {name[:3]} | " in err
    assert "odd level" in err


def test_exception_still_rendered(capfd):
    configure_logging()

    @logger.catch
    def boom():
        return 1 / 0

    boom()
    err = capfd.readouterr().err
    assert " | ERR | " in err
    assert "Traceback" in err
    assert "ZeroDivisionError" in err


def test_colors_on_tty_like_sink():
    sink = io.StringIO()
    logger.remove()
    logger.add(sink, format=stderr_format, colorize=True)
    logger.info("colored")
    assert "\x1b[" in sink.getvalue()


def test_no_colors_when_not_colorized():
    sink = io.StringIO()
    logger.remove()
    logger.add(sink, format=stderr_format, colorize=False)
    logger.info("plain")
    assert "\x1b[" not in sink.getvalue()


def test_log_file_format_unchanged():
    main()
    logger.remove()
    with open(os.environ["LOG_FILE"]) as f:
        content = f.read()
    assert re.search(
        r"\d{2}:\d{2}:\d{2}\.\d{3} \| INFO     \| "
        r"second_brain\.app:main:\d+ - Hello from second_brain!",
        content,
    ), content


def test_log_dir_is_under_home(tmp_home):
    assert log_dir() == tmp_home / ".second_brain"


@pytest.mark.parametrize("value", [None, ""])
def test_log_file_path_default(tmp_home, monkeypatch, value):
    if value is not None:
        monkeypatch.setenv("LOG_FILE", value)
    assert log_file_path() == tmp_home / ".second_brain" / "app.log"


@pytest.mark.parametrize("value", ["custom.log", "logs/dev.log"])
def test_log_file_path_relative_resolves_under_log_dir(tmp_home, monkeypatch, value):
    monkeypatch.setenv("LOG_FILE", value)
    assert log_file_path() == tmp_home / ".second_brain" / value


def test_log_file_path_absolute_used_as_is(tmp_home, tmp_path, monkeypatch):
    absolute = tmp_path / "elsewhere" / "abs.log"
    monkeypatch.setenv("LOG_FILE", str(absolute))
    assert log_file_path() == absolute


def test_log_file_path_expands_tilde(tmp_home, monkeypatch):
    monkeypatch.setenv("LOG_FILE", "~/custom.log")
    assert log_file_path() == tmp_home / "custom.log"


def test_configure_logging_writes_to_default_path_regardless_of_cwd(
    tmp_home, tmp_path, monkeypatch
):
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    configure_logging()
    logger.info("marker")
    logger.remove()
    assert "marker" in (tmp_home / ".second_brain" / "app.log").read_text()
    assert list(cwd.iterdir()) == []


def test_configure_logging_creates_missing_log_dir(tmp_home):
    assert not (tmp_home / ".second_brain").exists()
    configure_logging()
    logger.remove()
    assert (tmp_home / ".second_brain").is_dir()


def test_configure_logging_absolute_path_into_missing_dir(
    tmp_home, tmp_path, monkeypatch
):
    absolute = tmp_path / "elsewhere" / "nested" / "abs.log"
    monkeypatch.setenv("LOG_FILE", str(absolute))
    configure_logging()
    logger.info("abs marker")
    logger.remove()
    assert absolute.is_file()
    assert not (tmp_home / ".second_brain").exists()
