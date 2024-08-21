import logging
import sys
from .config import DEBUG

__all__ = ["debugf", "infof", "errorf", "watchdog"]

# 配置日志格式
log_format = "%(asctime)s.%(msecs)03d %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(log_format, date_format)

# 创建日志记录器
loggers = {
    "DEBUG": logging.getLogger("DEBUG"),
    "INFO": logging.getLogger("INFO"),
    "ERROR": logging.getLogger("ERROR"),
    "WATCHDOG": logging.getLogger("WATCHDOG")
}

# 配置日志输出
handlers = {
    "DEBUG": logging.StreamHandler(sys.stdout),
    "INFO": logging.StreamHandler(sys.stdout),
    "ERROR": logging.StreamHandler(sys.stderr),
    "WATCHDOG": logging.StreamHandler(sys.stderr)
}

levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "ERROR": logging.ERROR,
    "WATCHDOG": logging.INFO
}

for handler_name, handler in handlers.items():
    handler.setFormatter(formatter)
    handler.setLevel(levels[handler_name])
    loggers[handler_name].addHandler(handler)
    loggers[handler_name].setLevel(levels[handler_name])
    loggers[handler_name].propagate = False

def debugf(format, *args):
    if DEBUG:
        msg = format % args
        loggers["DEBUG"].debug(msg)
        return msg
    return None

def infof(format, *args):
    msg = format % args
    loggers["INFO"].info(msg)
    return msg

def errorf(format, *args):
    msg = format % args
    loggers["ERROR"].error(msg)
    return msg

def watchdog(msg):
    loggers["WATCHDOG"].info(msg)