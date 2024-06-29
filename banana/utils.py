from sqlalchemy import Engine

from .models import read_yaml, BananaTables, BananaTable, Config


def get_table_model(table_name: str, config: Config) -> BananaTable:
    data = read_yaml(config.tables_file)
    tables = BananaTables(**data)
    return tables[table_name]


def read_sql(statement, engine: Engine):
    with engine.connect() as conn:
        result = conn.execute(statement)
        rows = result.fetchall()
    return rows
