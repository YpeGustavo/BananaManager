from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, PositiveInt
import yaml


class Config(BaseModel):
    connection_string: str
    port: PositiveInt = 4000
    tables_file: str = "tables.yaml"
    title: str = "Banana Database Manager"


def read_yaml(file) -> dict:
    try:
        with open(file, "r", encoding="utf8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise Exception(f"Config file `{file}` not found.")
    except yaml.YAMLError as exc:
        raise Exception(f"Error parsing YAML config file: {exc}")


def load_config():
    data = read_yaml("config.yaml")
    return Config(**data)


config = load_config()

server = Flask(config.title)
server.config["SQLALCHEMY_DATABASE_URI"] = config.connection_string
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(server)


def read_sql(statement):
    with db.engine.connect() as conn:
        result = conn.execute(statement)
        rows = result.fetchall()
    return rows
