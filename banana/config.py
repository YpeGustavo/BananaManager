from pydantic import BaseModel, PositiveInt
import yaml


class Config(BaseModel):
    connection_string: str
    debug: bool = False
    port: PositiveInt = 4000
    tables_file: str = "tables.yaml"


with open("config.yaml", "r") as file:
    data = yaml.safe_load(file)
    CONFIG = Config(**data)
