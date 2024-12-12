from .models import BananaColumn, BananaGroup, BananaTable
from ..config import config
from ..errors import MultipleGroupsWithSameName, MultipleTablesWithSameName
from ..utils import read_yaml


class Tables:
    tables = None

    def __call__(self, group_name: str, table_name: str) -> BananaTable:
        return self.tables[group_name]["tables"][table_name]

    def refresh_models(self) -> dict[str, dict]:
        # Read every folder
        self.tables = dict()
        for table_path in config.tablePaths:
            for suffix in ("*.yaml", "*.yml"):

                # Read every group
                for file in table_path.rglob(suffix):
                    if file.stem in self.tables:
                        raise MultipleGroupsWithSameName(file.stem)
                    data = read_yaml(file)
                    group = BananaGroup(**data)
                    self.tables[file.stem] = {
                        "group_name": group.groupName or file.stem,
                        "display_order": group.displayOrder,
                        "tables": dict(),
                    }

                    # Read every table
                    for table in group.tables:
                        if table.name in self.tables[file.stem]:
                            raise MultipleTablesWithSameName(table.name)
                        self.tables[file.stem]["tables"][table.name] = table


tables = Tables()
