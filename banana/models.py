from typing import Optional, Self

from pydantic import BaseModel, PositiveInt, model_validator


class Config(BaseModel):
    connection_string: str
    debug: bool = False
    port: PositiveInt = 4000
    tables_file: str = "tables.yaml"


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
    pretty_name: Optional[str] = None
    columns: Optional[list[BananaColumn]] = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.pretty_name is None:
            self.pretty_name = self.name
        return self
