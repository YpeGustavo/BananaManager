from functools import cached_property
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator, PositiveInt

from ..config import config
from ...queries import create_foreign_key_options, get_primary_key


class BananaBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BananaDataType(BananaBaseModel):
    type: Literal[
        "default",
        "enumerator",
        "foreign",
        "color",
        "image",
        "list",
    ] = "default"
    data: Optional[dict] = None


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
    dataType: BananaDataType = Field(default_factory=BananaDataType)
    columnDef: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name
        return self

    @cached_property
    def data(self) -> dict[str, str]:
        match self.dataType.type:
            case "foreign":
                return create_foreign_key_options(
                    table_name=self.dataType.data["tableName"],
                    schema_name=self.dataType.data["schemaName"],
                    key_column=self.dataType.data["columnDisplay"],
                    value_column=self.dataType.data["columnName"],
                )
            case _:
                return self.dataType.data

    @cached_property
    def column_def(self) -> dict[str, str]:
        match self.dataType.type:
            case "foreign":
                col_def = {
                    "headerName": self.display_name,
                    "field": self.name,
                    "cellEditor": "agSelectCellEditor",
                    "cellEditorParams": {"values": [self.data[d] for d in self.data]},
                }
                col_def.update(self.columnDef)
                return col_def

            case _:
                col_def = {"headerName": self.display_name, "field": self.name}
                col_def.update(self.columnDef)
                return col_def


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
