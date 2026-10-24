import io
import os
import re
from pathlib import Path

import pytest
from loguru import logger

from second_brain.app import LOG_FORMAT, configure_logging, main

LINE_PREFIX = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| INF \| ")


@pytest.fixture
def notice_level():
    """Register a custom NOTICE level once; loguru levels can't be re-created."""
    try:
        logger.level("NOTICE")
    except ValueError:
        logger.level("NOTICE", no=25)


def test_main_logs_greeting(capfd):
    main()
    captured = capfd.readouterr()
    assert "Hello from second_brain!" in captured.err


def test_console_format(capfd):
    main()
    err = capfd.readouterr().err
    assert LINE_PREFIX.match(err)


def test_file_format():
    main()
    content = Path(os.environ["LOG_FILE"]).read_text()
    assert LINE_PREFIX.match(content)


def test_console_and_file_same_format(capfd):
    main()
    err = capfd.readouterr().err
    content = Path(os.environ["LOG_FILE"]).read_text()
    assert err == content


@pytest.mark.parametrize(
    ("level", "shorthand"),
    [
        ("TRACE", "TRC"),
        ("DEBUG", "DBG"),
        ("INFO", "INF"),
        ("SUCCESS", "SUC"),
        ("WARNING", "WRN"),
        ("ERROR", "ERR"),
        ("CRITICAL", "CRT"),
        ("NOTICE", "NOTICE"),
    ],
)
@pytest.mark.usefixtures("notice_level")
def test_level_shorthand(capfd, monkeypatch, level, shorthand):
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    configure_logging()
    logger.log(level, "message")
    err = capfd.readouterr().err
    assert f" | {shorthand} | " in err


def test_level_shorthand_colored():
    configure_logging()
    sink = io.StringIO()
    logger.add(sink, format=LOG_FORMAT, colorize=True)
    logger.info("message")
    assert re.search(r"\x1b\[[\d;]*mINF\x1b\[0m", sink.getvalue())
