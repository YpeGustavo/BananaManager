from .models import BananaGroup
from ..config import config
from ..errors import MultipleGroupsWithSameName, MultipleTablesWithSameName
from ..utils import read_yaml


def __read_models() -> dict[str, dict]:
    # Read every folder
    models = dict()
    for table_path in config.tablePaths:
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
                    models[file.stem]["tables"][table.name] = table

    return models


tables = __read_models()
