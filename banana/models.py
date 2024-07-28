import json
from typing import Optional

from pydantic import BaseModel, model_validator, PositiveInt

from .utils import config


class BananaOrderBy(BaseModel):
    column: str
    desc: bool = False


class BananaForeignKey(BaseModel):
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


class BananaPrimaryKey(BaseModel):
    name: str
    display_name: Optional[str] = None
    hide: bool = False
    filter: bool = True
    sortable: bool = True

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaColumn(BaseModel):
    name: str
    display_name: Optional[str] = None
    foreign_key: Optional[BananaForeignKey] = None
    editable: bool = True
    filter: bool = True
    sortable: bool = True

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaTable(BaseModel):
    name: str
    primary_key: BananaPrimaryKey
    display_name: Optional[str] = None
    schema_name: Optional[str] = None
    columns: Optional[list[BananaColumn]] = None
    order_by: Optional[list[BananaOrderBy]] = None
    limit: Optional[PositiveInt] = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.display_name is None:
            self.display_name = self.name
        return self


class BananaGroup(BaseModel):
    tables: list[BananaTable]
    group_name: Optional[str] = None
    display_order: Optional[int] = None


def get_table_model(table_name: str, group_name: str) -> BananaTable:
    json_dir = config.data_path.joinpath("models.json")
    with open(json_dir, "r") as f:
        models = json.load(f)
        table = BananaTable(**models[group_name]["tables"][table_name])
    return table
