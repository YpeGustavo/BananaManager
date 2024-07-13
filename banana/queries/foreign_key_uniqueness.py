from sqlalchemy import MetaData, Table, select, func

from ..errors import InvalidBananaForeignKey
from ..models import BananaTables
from ..utils import read_sql, read_yaml, config, db


def check_foreign_key_uniqueness() -> bool:
    metadata = MetaData()
    data = read_yaml(config.tables_file)
    tables = BananaTables(**data)

    for table in tables.tables:
        for column in table.columns:
            if column.foreign_key is not None:
                foreign_table = Table(
                    column.foreign_key.table_name,
                    metadata,
                    schema=column.foreign_key.schema_name,
                    autoload_with=db.engine,
                )

                stmt = select(
                    (
                        func.count("*")
                        == func.count(
                            func.distinct(
                                foreign_table.c[column.foreign_key.column_name]
                            )
                        )
                    ),
                    (
                        func.count("*")
                        == func.count(
                            func.distinct(
                                foreign_table.c[column.foreign_key.column_display]
                            )
                        )
                    ),
                )

                rows = read_sql(stmt)

                if not rows[0][0]:
                    raise InvalidBananaForeignKey(
                        foreign_table.name,
                        column.foreign_key.column_name,
                    )
                elif not rows[0][1]:
                    raise InvalidBananaForeignKey(
                        foreign_table.name,
                        column.foreign_key.column_display,
                    )
