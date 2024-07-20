from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, DirectoryPath, PositiveInt, field_validator
import yaml


class Config(BaseModel):
    connection_string: str
    data_path: str = DirectoryPath("data")
    port: PositiveInt = 4000
    table_paths: list[DirectoryPath] = [DirectoryPath("tables")]
    title: str = "Banana Database Manager"

    @field_validator("data_path")
    def _validate_date_path(value):
        return DirectoryPath(value)


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
