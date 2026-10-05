"""Terminal messages with a volume knob (log level).

Set LOG_LEVEL in .env:
    DEBUG    everything: every chart tick and every web request (for hunting bugs)
    INFO     default: start-up, session start/end, warnings and errors
    WARNING  problems only (e.g. during real experiments)

Use in a module:
    from trade.utils.logs import get_logger
    logger = get_logger("graph")
    logger.debug("...")   # hidden unless LOG_LEVEL=DEBUG
    logger.error("...")   # always shown
"""
import logging
import os

_FORMAT = "%(asctime)s %(levelname)-7s [%(name)s] %(message)s"


def setup_logging():
    """Apply LOG_LEVEL to TradeSim's messages and to the web server's request lines."""
    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").strip().upper(), logging.INFO)

    logger = logging.getLogger("tradesim")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_FORMAT, datefmt="%H:%M:%S"))
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False

    # The web server writes one line per request, several every tick: only in DEBUG
    logging.getLogger("werkzeug").setLevel(logging.INFO if level <= logging.DEBUG else logging.WARNING)
    return level


def get_logger(name):
    """Logger for one part of the app, shown in the terminal as [tradesim.<name>]."""
    return logging.getLogger(f"tradesim.{name}")
