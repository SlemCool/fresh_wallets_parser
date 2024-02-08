import logging
import os
from logging.handlers import RotatingFileHandler

_log_format = (
    "%(asctime)s - [%(levelname)s] - %(name)s - "
    "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)
if not os.path.isdir("logs"):
    os.mkdir("logs")


def get_file_handler():
    file_handler = RotatingFileHandler(
        "logs/FWParser.log",
        encoding="utf-8",
        maxBytes=3 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger
