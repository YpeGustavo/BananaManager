from .compile import tables
from .models import BananaColumn, BananaTable


def get_table_model(group_name: str, table_name: str) -> BananaTable:
    return tables[group_name]["tables"][table_name]
