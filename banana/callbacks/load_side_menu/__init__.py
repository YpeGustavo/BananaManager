import json

import dash_mantine_components as dmc

from ...core.instances import config
from ...core.utils import split_pathname


class LoadSideMenuCallback:
    def __init__(self, pathname: str):
        self.selected_group, self.selected_table = split_pathname(pathname)

    def _get_models(self) -> list[tuple]:
        json_dir = config.dataPath.joinpath("models.json")
        with open(json_dir, "r") as f:
            models = json.load(f)

        groups = sorted(models, key=lambda d: models[d]["display_order"])

        menu = []
        for group in groups:
            tables = []
            for table in models[group]["tables"]:
                tables.append(
                    {
                        "table_name": table,
                        "table_display_name": models[group]["tables"][table][
                            "display_name"
                        ],
                    }
                )

            menu.append(
                {
                    "group_name": group,
                    "group_display_name": models[group]["group_name"],
                    "tables": tables,
                }
            )

        return menu

    @property
    def menu(self) -> list:
        models = self._get_models()

        links = []
        for group in models:
            links.append(
                dmc.Divider(
                    label=group["group_display_name"],
                    mt=20,
                    color=config.theme,
                    styles={
                        "label": {"color": dmc.DEFAULT_THEME["colors"][config.theme][1]}
                    },
                )
            )
            for table in group["tables"]:
                link = dmc.Button(
                    table["table_display_name"],
                    variant=(
                        "filled"
                        if (group["group_name"] == self.selected_group)
                        and (table["table_name"] == self.selected_table)
                        else "subtle"
                    ),
                    color=config.theme,
                    radius="md",
                    size="xs",
                    styles={"inner": {"justify-content": "left", "color": "white"}},
                    id={
                        "component": "menu-item",
                        "group": group["group_name"],
                        "table": table["table_name"],
                    },
                )
                links.append(link)

        return links
