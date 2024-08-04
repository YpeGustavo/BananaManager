import json

from sqlalchemy import MetaData, Table, select, func

from ..errors import (
    InvalidForeignKey,
    MultipleGroupsWithSameName,
    MultipleTablesWithSameName,
)
from ..models import BananaGroup, BananaTable
from ..utils import read_sql, read_yaml, config, db


class InitApp:
    def refresh(self) -> None:
        self._create_data_folder()
        self._create_models_manifest()

    def _check_foreign_key_uniqueness(self, table: BananaTable) -> bool:
        metadata = MetaData()

        for column in table.columns:
            if column.foreign_key is not None:
                foreign_table = Table(
                    column.foreign_key.table_name,
                    metadata,
                    schema=column.foreign_key.schema_name,
                    autoload_with=db.engine,
                )

                query = select(
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

                rows = read_sql(query)

                if not rows[0][0]:
                    raise InvalidForeignKey(
                        foreign_table.name,
                        column.foreign_key.column_name,
                    )
                elif not rows[0][1]:
                    raise InvalidForeignKey(
                        foreign_table.name,
                        column.foreign_key.column_display,
                    )

    def _create_data_folder(self) -> None:
        config.data_path.mkdir(parents=True, exist_ok=True)

    def _create_models_manifest(self) -> None:
        models = self._read_models()
        with open(config.data_path.joinpath("models.json"), "w") as f:
            json.dump(models, f)

    def _read_models(self) -> dict[str, dict]:
        # Read every folder
        models = dict()
        for table_path in config.table_paths:
            for suffix in ("*.yaml", "*.yml"):

                # Read every group
                for file in table_path.rglob(suffix):
                    if file.stem in models:
                        raise MultipleGroupsWithSameName(file.stem)
                    data = read_yaml(file)
                    group = BananaGroup(**data)
                    models[file.stem] = {
                        "group_name": group.group_name or file.stem,
                        "display_order": group.display_order,
                        "tables": dict(),
                    }

                    # Read every table
                    for table in group.tables:
                        if table.name in models[file.stem]:
                            raise MultipleTablesWithSameName(table.name)
                        self._check_foreign_key_uniqueness(table)
                        models[file.stem]["tables"][table.name] = table.model_dump()

        return models
