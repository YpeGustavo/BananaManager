import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .models import Config
from ..utils import read_yaml


def __get_config() -> Config:
    data = read_yaml("config.yaml")
    return Config(**data)


def __get_logger(config: Config) -> logging.Logger:
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    errorlog_path = config.dataPath.joinpath("error.log")

    handler = RotatingFileHandler(errorlog_path, maxBytes=10000, backupCount=1)
    handler.setLevel(logging.ERROR)
    handler.setFormatter(formatter)

    logger = logging.getLogger("banana-manager")
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    return logger


def __get_server(config: Config, logger: logging.Logger) -> Flask:
    server = Flask(config.title)
    server.config["SQLALCHEMY_DATABASE_URI"] = config.connection_string
    server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    @server.errorhandler(Exception)
    def handle_exception(e):
        logger.error(str(e), exc_info=True)
        return "An internal error occurred", 500

    return server


config = __get_config()
logger = __get_logger(config)
server = __get_server(config, logger)
db = SQLAlchemy(server)
