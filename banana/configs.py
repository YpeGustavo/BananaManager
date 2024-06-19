from pydantic import BaseModel, PositiveInt
import yaml


class Config(BaseModel):
    connection_string: str
    debug: bool = True
    port: PositiveInt = 8050
    tables_file: str = "tables.yaml"


with open("config.yaml", "r") as file:
    data = yaml.safe_load(file)
    CONFIG = Config(**data)

with open(CONFIG.tables_file, "r") as file:
    TABLES = yaml.safe_load(file)
