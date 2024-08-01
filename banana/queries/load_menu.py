import json

from dash import html

from ..utils import config, split_pathname


class LoadMenuCallback:
    def __init__(self, pathname: str):
        self.selected_group, self.selected_table = split_pathname(pathname)

    def _get_models(self) -> list[tuple]:
        json_dir = config.data_path.joinpath("models.json")
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
            links.append(html.Hr(className="menu-hr"))
            label = html.Div(group["group_display_name"], className="menu-group")
            links.append(label)
            for table in group["tables"]:
                className = "menu-item"
                if (group["group_name"] == self.selected_group) and (
                    table["table_name"] == self.selected_table
                ):
                    className += " selected"

                link = html.A(
                    table["table_display_name"],
                    href=f'/{group["group_name"]}/{table["table_name"]}',
                    className=className,
                )
                links.append(link)

        return links
