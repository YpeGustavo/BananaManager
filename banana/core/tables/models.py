import json
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator, PositiveInt
from sqlalchemy import inspect

from ..config import config, db


class BananaBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BananaOrderBy(BananaBaseModel):
    column: str
    desc: bool = False


class BananaForeignKey(BananaBaseModel):
    table_name: str
    column_name: str
    column_display: Optional[str] = None
    schema_name: Optional[str] = None
    order_by: Optional[list[BananaOrderBy]] = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.column_display is None:
            self.column_display = self.column_name
        return self


class BananaPrimaryKey(BananaBaseModel):
    columnDef: dict[str, Any] = Field(default_factory=dict)
    display_name: Optional[str] = None
    name: Optional[str] = None


class BananaColumn(BananaBaseModel):
    name: str
    display_name: Optional[str] = None
    foreign_key: Optional[BananaForeignKey] = None
    columnDef: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaTable(BananaBaseModel):
    name: str
    display_name: Optional[str] = None
    schema_name: Optional[str] = None
    primary_key: Optional[BananaPrimaryKey] = None
    columns: Optional[list[BananaColumn]] = None
    order_by: Optional[list[BananaOrderBy]] = None
    limit: Optional[PositiveInt] = None
    defaultColDef: dict[str, Any] = Field(default_factory=dict)
    gridOptions: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name

        # Apply default configs
        self.defaultColDef = {**config.defaultColDef, **self.defaultColDef}
        self.gridOptions = {**config.defaultGridOptions, **self.gridOptions}

        return self

    def _primary_key_validation(self):
        # Get primary key
        inspector = inspect(db.engine)
        pk_info = inspector.get_pk_constraint(self.name, self.schema_name)

        # Assert if there is a primary key with one column
        if not pk_info["constrained_columns"]:
            raise AssertionError(f"Table '{self.name}' has no primary key.")
        elif len(pk_info["constrained_columns"]) > 1:
            raise AssertionError(
                f"Table '{self.name}' primary key must have only one column."
            )

        # Fix names
        if self.primary_key is None:
            self.primary_key = BananaPrimaryKey()
        self.primary_key.name = pk_info["constrained_columns"][0]
        if self.primary_key.display_name is None:
            self.primary_key.display_name = self.primary_key.name


class BananaGroup(BananaBaseModel):
    tables: list[BananaTable]
    group_name: Optional[str] = None
    display_order: Optional[int] = None
