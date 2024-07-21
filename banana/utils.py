from os import environ
from typing import Optional

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel, DirectoryPath, PositiveInt, field_validator, Field
from sqlalchemy.engine.url import URL
import yaml


class Connection(BaseModel):
    drivername: Optional[str] = None
    username: Optional[str] = Field(default=None, validate_default=True)
    password: Optional[str] = Field(default=None, validate_default=True)
    host: Optional[str] = None
    port: Optional[PositiveInt] = None
    database: Optional[str] = None

    @field_validator("username")
    def _validate_username(value):
        if value is None:
            value = environ.get("BANANA_USERNAME", None)
        return value

    @field_validator("password")
    def _validate_password(value):
        if value is None:
            return environ.get("BANANA_PASSWORD", None)
        return value


class Config(BaseModel):
    connection: Connection
    data_path: str = DirectoryPath("data")
    port: PositiveInt = 4000
    table_paths: list[DirectoryPath] = [DirectoryPath("tables")]
    title: str = "Banana Database Manager"

    @field_validator("data_path")
    def _validate_date_path(value):
        return DirectoryPath(value)

    @property
    def connection_string(self) -> str:
        return URL(
            drivername=self.connection.drivername,
            username=self.connection.username,
            password=self.connection.password,
            host=self.connection.host,
            port=self.connection.port,
            database=self.connection.database,
            query={},
        )


def read_yaml(file) -> dict:
    try:
        with open(file, "r", encoding="utf8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise Exception(f"Config file `{file}` not found.")
    except yaml.YAMLError as exc:
        raise Exception(f"Error parsing YAML config file: {exc}")


def __load_config():
    data = read_yaml("config.yaml")
    return Config(**data)


config = __load_config()

server = Flask(config.title)
server.config["SQLALCHEMY_DATABASE_URI"] = config.connection_string
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(server)


def read_sql(statement):
    with db.engine.connect() as conn:
        result = conn.execute(statement)
        rows = result.fetchall()
    return rows
