import dash_mantine_components as dmc

from ...models import BananaTable, get_table_model
from ...utils import split_pathname


class OpenInsertModalCallback:
    def __init__(self, pathname: str):
        group_name, table_name = split_pathname(pathname)
        banana_table = get_table_model(group_name, table_name)
        self.fields = self.__get_fields_metadata(banana_table)

    def __get_fields_metadata(self, table: BananaTable):
        fields = [
            {
                "display_name": table.primary_key.display_name,
                "name": table.primary_key.name,
            }
        ]
        for col in table.columns:
            fields.append({"display_name": col.display_name, "name": col.name})
        return fields

    def __get_field(self, field: dict[str, str]):
        return [
            dmc.Text(field["display_name"]),
            dmc.TextInput(
                id={"component": "form-item", "column": field["name"]},
                radius="md",
            ),
        ]

    @property
    def form(self):
        fields = []
        for field in self.fields:
            fields += self.__get_field(field)
        return fields
