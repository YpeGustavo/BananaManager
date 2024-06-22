from typing import Optional, Self

from pydantic import BaseModel, model_validator
import yaml

from .config import CONFIG


class BananaColumn(BaseModel):
    name: str
    pretty_name: Optional[str] = None
    datatype: Optional[str] = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.pretty_name is None:
            self.pretty_name = self.name
        return self


class BananaTable(BaseModel):
    name: str
    primary_key: str
    pretty_name: Optional[str] = None
    columns: Optional[list[BananaColumn]] = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.pretty_name is None:
            self.pretty_name = self.name
        return self


try:
    with open(CONFIG.tables_file, "r") as file:
        data = yaml.safe_load(file)
        TABLES = [BananaTable(**table) for table in data["tables"]]
except FileNotFoundError:
    raise Exception(f"Config file {CONFIG.tables_file} not found.")
except yaml.YAMLError as exc:
    raise Exception(f"Error parsing YAML config file: {exc}")
