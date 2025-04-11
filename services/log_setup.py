import sys
import logging
import colorlog


def setup_logging(level=logging.DEBUG):
    """Configure colorized logging to be used throughout the application."""
    LOGGING_FMT_COLOR = "%(log_color)s%(asctime)s [%(levelname)s] %(message)s"
    formatter = colorlog.ColoredFormatter(
        LOGGING_FMT_COLOR,
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Clear existing handlers and add our configured one
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(level)

    return root_logger
