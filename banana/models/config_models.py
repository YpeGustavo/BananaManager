from os import environ
from typing import Any, Optional

from pydantic import BaseModel, DirectoryPath, PositiveInt, Field, field_validator
from sqlalchemy.engine.url import URL


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
    dataPath: str = DirectoryPath("data")
    port: PositiveInt = 4000
    tablePaths: list[DirectoryPath] = [DirectoryPath("tables")]
    title: str = "Banana Database Manager"
    theme: str = "cyan"
    defaultColDef: dict[str, Any] = Field(default_factory=dict, validate_default=True)
    defaultGridOptions: dict[str, Any] = Field(default_factory=dict)

    @field_validator("dataPath")
    def _validate_date_path(value):
        return DirectoryPath(value)

    @field_validator("defaultColDef")
    def _validate_defaultColDef(value):
        default = {"editable": True, "filter": True, "sortable": True}
        return {**default, **value}

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
