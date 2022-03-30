"""
Methods to: provide and manage central logging utility
"""
import logging
import sys
from copy import copy

ENABLE_DEBUG = False

class ExitHandler(logging.Handler):
    """
    Add custom logging handler to exit on certain logging level
    """
    def emit(self, record):
        logging.shutdown()
        sys.exit(1)

class FastPlottingLoggerFormatter(logging.Formatter):
    """
    A custom formatter that colors the levelname on request
    """
    # color names to indices
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }

    level_map = {
        logging.DEBUG: (None, 'yellow', False),
        logging.INFO: (None, 'blue', False),
        logging.WARNING: ('yellow', 'black', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }
    csi = '\x1b['
    reset = '\x1b[0m'

    # Define default format string
    def __init__(self, fmt='%(levelname)s in %(pathname)s:%(lineno)d:\n%(message)s',
                 datefmt=None, style='%', color=False):
        logging.Formatter.__init__(self, fmt, datefmt, style)
        self.color = color

    def format(self, record):
        # Copy the record so the global format is kept
        cached_record = copy(record)
        requ_color = self.color
        # Could be a lambda so check for callable property
        if callable(self.color):
            requ_color = self.color()
        # Make sure levelname takes same space for all cases
        cached_record.levelname = f"{cached_record.levelname:8}"
        # Colorize if requested
        if record.levelno in self.level_map and requ_color:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                cached_record.levelname = "".join((self.csi, ';'.join(params), "m",
                                                   cached_record.levelname,
                                                   self.reset))
        return logging.Formatter.format(self, cached_record)


def reconfigure_logging(debug, *names):
    if not names:
        # set as default
        ENABLE_DEBUG = debug
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    else:
        loggers = [logging.getLogger(name) for name in names]
    for l in loggers:
        l.setLevel(logging.DEBUG)

def configure_logger(name="FastPlottingBase", debug=False, logfile=None):
    """
    Basic configuration adding a custom formatted StreamHandler and turning on
    debug info if requested.
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return

    # Turn on debug info only on request
    if debug or ENABLE_DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    formatter = FastPlottingLoggerFormatter(color=lambda : getattr(sh.stream, 'isatty', None))

    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # Add logfile on request
    if logfile is not None:
        # Specify output format
        fh = logging.FileHandler(logfile)
        fh.setFormatter(FastPlottingLoggerFormatter())
        logger.addHandler(fh)

    # Add handler to exit at critical. Do this as the last step so all former
    # logger flush before aborting
    logger.addHandler(ExitHandler(logging.CRITICAL))

def get_logger(name="FastPlottingBase"):
    """
    Get the global logger for this package and set handler together with formatters.
    """
    configure_logger(name, ENABLE_DEBUG, None)
    return logging.getLogger(name)
