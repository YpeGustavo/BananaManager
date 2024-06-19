import yaml

from .models import BananaTable, Config


with open("config.yaml", "r") as file:
    data = yaml.safe_load(file)
    CONFIG = Config(**data)

with open(CONFIG.tables_file, "r") as file:
    data = yaml.safe_load(file)
    TABLES = [BananaTable(**table) for table in data["tables"]]
    print("\n", TABLES)
