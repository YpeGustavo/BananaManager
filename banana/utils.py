from .models import read_yaml, BananaTables, BananaTable, Config


def get_table_model(table_name: str, config: Config) -> BananaTable:
    data = read_yaml(config.tables_file)
    tables = BananaTables(**data)
    return tables[table_name]
