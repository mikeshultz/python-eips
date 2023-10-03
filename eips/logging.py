import logging


class ConsoleStyle:
    """Console coloring and styles"""

    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    CRITICAL = "\033[31m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"  # Stop all styling


fmts = {
    logging.CRITICAL: "{}%(levelname)s{} \t %(message)s".format(
        ConsoleStyle.CRITICAL, ConsoleStyle.END
    ),
    logging.ERROR: "{}%(levelname)s{} \t %(message)s".format(
        ConsoleStyle.ERROR, ConsoleStyle.END
    ),
    logging.WARNING: "{}%(levelname)s{} \t %(message)s".format(
        ConsoleStyle.WARNING, ConsoleStyle.END
    ),
    logging.INFO: "{}%(levelname)s{} \t\t %(message)s".format(
        ConsoleStyle.OKGREEN, ConsoleStyle.END
    ),
    logging.DEBUG: "{}%(levelname)s{} \t %(message)s".format(
        ConsoleStyle.OKBLUE, ConsoleStyle.END
    ),
}


class ColoredStyle(logging.PercentStyle):
    """Text styling for the ColoredFormatter.

    Ref: https://github.com/python/cpython/blob/5e7ea95d9d5c3b80a67ffbeebd76ce4fc327dd8e/Lib/logging/__init__.py#L440
    """

    def _format(self, record: logging.LogRecord) -> str:
        return fmts.get(record.levelno, self._fmt) % record.__dict__


class ColoredFormatter(logging.Formatter):
    """Formatter that will use the ColoredStyle class"""

    def __init__(
        self,
        fmt: str = "",
        datefmt: str = "",
        style: str = "%",
        validate: bool = True,
    ) -> None:
        self._style = ColoredStyle(fmt)

        if validate:
            self._style.validate()

        self._fmt = self._style._fmt
        self.datefmt = datefmt


parent_logger = logging.getLogger()

# Create and add a handler for console output
console_handler = logging.StreamHandler()
formatter = ColoredFormatter()
console_handler.setFormatter(formatter)
parent_logger.addHandler(console_handler)


def setDebugLogging() -> None:
    console_handler.setLevel(logging.DEBUG)
    parent_logger.setLevel(logging.DEBUG)


console_handler.setLevel(logging.INFO)
parent_logger.setLevel(logging.INFO)


def getLogger(name: str) -> logging.Logger:
    return parent_logger.getChild(name)


def loggingShutdown() -> None:
    return logging.shutdown()
