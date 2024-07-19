from dash import html
from sqlalchemy import Table, MetaData, select, func

from ..utils import read_sql, config, db, server


class LoadMenuCallback:
    def __init__(self, pathname: str):
        try:
            _, self.selected_group, self.selected_table = pathname.split("/")
        except ValueError:
            self.selected_group = None
            self.selected_table = None

    def get_result(self) -> list[tuple]:
        with server.app_context():
            metadata = MetaData()
            table = Table(
                config.indexing_table,
                metadata,
                schema=config.indexing_schema,
                autoload_with=db.engine,
            )

            # Columns
            table_name = table.c.table_name
            table_display_name = table.c.table_display_name
            group_name = table.c.group_name
            group_display_name = table.c.group_display_name
            group_display_order = table.c.group_display_order

            query = (
                select(
                    table_name,
                    func.coalesce(table_display_name, table_name).label(
                        "table_display_name"
                    ),
                    group_name,
                    func.coalesce(group_display_name, group_name).label(
                        "group_display_name"
                    ),
                )
                .select_from(table)
                .order_by(
                    group_display_order, func.coalesce(group_display_name, group_name)
                )
            )

            result = read_sql(query)

        return result

    def get_groups(self, result: list[tuple]) -> dict[str, str]:
        groups: dict[str, list[str]] = {}
        for row in result:
            group_name = row[3]
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(row)

        return groups

    def get_menu(self, groups: dict[str, str]) -> list:
        menu = []
        for group in groups:
            menu.append(html.Hr(className="menu-hr"))
            label = html.Div(group.upper(), className="menu-group")
            menu.append(label)
            for row in groups[group]:
                className = "menu-item"
                if (row[2] == self.selected_group) and (row[0] == self.selected_table):
                    className += " selected"

                link = html.A(
                    row[1],
                    href=f"/{row[2]}/{row[0]}",
                    className=className,
                )
                menu.append(link)

        return menu

    @property
    def menu(self) -> list:
        result = self.get_result()
        groups = self.get_groups(result)
        return self.get_menu(groups)
