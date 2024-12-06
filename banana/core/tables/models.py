from functools import cached_property
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator, PositiveInt

from ..config import config
from ...queries import get_primary_key


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

    @cached_property
    def primary_key(self) -> str:
        return get_primary_key(self.name, self.schema_name)


class BananaGroup(BananaBaseModel):
    tables: list[BananaTable]
    group_name: Optional[str] = None
    display_order: Optional[int] = None
