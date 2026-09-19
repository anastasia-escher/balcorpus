import logging
import os
import sys

# The stdout of the container's main process.  A command started with
# `docker compose exec` gets a stream of its own, so whatever it prints lands
# in that terminal and never shows up in `docker compose logs`.  Writing to the
# main process's stdout as well puts the output in both places.
CONTAINER_STDOUT = '/proc/1/fd/1'

# The main process writes its stdout and its stderr to two different streams,
# and both end up in `docker compose logs`.  A process that inherited either of
# them is already being logged, so it must not add a second handler.
CONTAINER_STREAMS = ('/proc/1/fd/1', '/proc/1/fd/2')


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    magenta = "\x1b[35;20m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"
    format = "%(name)s:  %(levelname)s ----- %(message)s"

    FORMATS = {
        logging.DEBUG: magenta + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def container_log_handler():
    """A handler that writes into the container's own log stream.

    Returns None when there is nothing to gain: outside Docker the path does
    not exist, and in the main process our output already goes there, so a
    second handler would print every line twice.
    """
    try:
        ours = os.fstat(sys.stderr.fileno())
        for stream in CONTAINER_STREAMS:
            if os.path.samestat(os.stat(stream), ours):
                return None

        handler = logging.FileHandler(CONTAINER_STDOUT)
    except OSError:
        return None

    handler.setLevel(logging.DEBUG)
    handler.setFormatter(CustomFormatter())
    return handler


logger = logging.getLogger("API")
logger.setLevel(logging.DEBUG)


logger.handlers = []
logging.getLogger().handlers = []

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.propagate = False
logger.addHandler(ch)

container_handler = container_log_handler()
if container_handler is not None:
    logger.addHandler(container_handler)
