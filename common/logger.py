# logger.py

import logging
import inspect
import os

from common.config import Config as config

# Configure the logging module
logging.basicConfig(
    level=logging.getLevelName(config.LOG_LEVEL),
    # level=logging.getLevelName(config.log_level.upper()),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Output logs to sys.stderr
)


def log_message(level, message):
    logger = logging.getLogger(__name__)

    # Get the current frame and go back one step to the caller
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_info = inspect.getframeinfo(caller_frame)

    # Get only the last part of the file path
    filename = os.path.basename(caller_info.filename)

    # Add caller's file and line number to the message
    enhanced_message = f"{filename}:{caller_info.lineno} - {message}"

    log_method = getattr(logger, level.lower(), None)
    if log_method is not None:
        log_method(enhanced_message)
    else:
        raise ValueError(f"Invalid log level: {level}")


__all__ = ["log_message"]
