import logging
import os
from ..config import DEBUG

# Custom log formats
log_format = "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Set up loggers with custom formats and colors
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO, format=log_format, datefmt=date_format)

# Add color to the log levels
class CustomFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: "\033[1;33m",  # Yellow
        logging.INFO: "\033[1;34m",   # Blue
        logging.ERROR: "\033[1;31m",  # Red
        'ComfyUI': "\033[1;35m"       # Magenta for WatchDog
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.LEVEL_COLORS.get(record.levelno, "")
        levelname = record.levelname
        if levelname == 'INFO' and hasattr(record, 'watchdog'):
            log_color = self.LEVEL_COLORS['ComfyUI']
            levelname = "ComfyUI"
        record.levelname = f"{log_color}[ {levelname} ]{self.RESET}"
        return super().format(record)

formatter = CustomFormatter(log_format, date_format)

# Setting up different loggers
debug_logger = logging.getLogger("debug")
info_logger = logging.getLogger("info")
error_logger = logging.getLogger("error")
watchdog_logger = logging.getLogger("watchdog")

# Apply the formatter
for logger in [debug_logger, info_logger, error_logger, watchdog_logger]:
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

# Log functions
def debugf(format_str, *args):
    if DEBUG:
        msg = format_str % args
        debug_logger.debug(msg)
        return msg
    return ""

def infof(format_str, *args):
    msg = format_str % args
    info_logger.info(msg)
    return msg

def errorf(format_str, *args):
    msg = format_str % args
    error_logger.error(msg)
    return msg

def watchdog(msg):
    watchdog_logger.info(msg, extra={'watchdog': True})

