import logging
import sys
from .config import DEBUG

# 配置日志格式
log_format = "%(asctime)s.%(msecs)03d %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(log_format, date_format)

# 创建日志记录器
debug_logger = logging.getLogger("DEBUG")
info_logger = logging.getLogger("INFO")
error_logger = logging.getLogger("ERROR")
watchdog_logger = logging.getLogger("WATCHDOG")

# 配置日志输出
debug_handler = logging.StreamHandler(sys.stdout)
debug_handler.setFormatter(formatter)
debug_handler.setLevel(logging.DEBUG)

info_handler = logging.StreamHandler(sys.stdout)
info_handler.setFormatter(formatter)
info_handler.setLevel(logging.INFO)

error_handler = logging.StreamHandler(sys.stderr)
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)

watchdog_handler = logging.StreamHandler(sys.stderr)
watchdog_handler.setFormatter(formatter)
watchdog_handler.setLevel(logging.INFO)

# 设置日志记录器的处理程序和级别
debug_logger.addHandler(debug_handler)
debug_logger.setLevel(logging.DEBUG)

info_logger.addHandler(info_handler)
info_logger.setLevel(logging.INFO)

error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)

watchdog_logger.addHandler(watchdog_handler)
watchdog_logger.setLevel(logging.INFO)

# 设置日志记录器的格式
debug_logger.propagate = False
info_logger.propagate = False
error_logger.propagate = False
watchdog_logger.propagate = False

def debugf(format, *args):
    if DEBUG:
        msg = format % args
        debug_logger.debug(msg)
        return msg
    return ""

def infof(format, *args):
    msg = format % args
    info_logger.info(msg)
    return msg

def errorf(format, *args):
    msg = format % args
    error_logger.error(msg)
    return msg

def watchdog(msg):
    watchdog_logger.info(msg)