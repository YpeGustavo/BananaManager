import json

from dash import html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from ..history import LogType, get_history
from ..models import get_table_model
from ..utils import split_pathname


def t(text) -> str:
    text = str(text)
    if len(text) > 12:
        return text[:12] + "…"
    return text


class LoadHistoryCallback:
    def __init__(self, pathname: str):
        group_name, table_name = split_pathname(pathname)
        banana_table = get_table_model(group_name, table_name)

    def __text(self, upper, lower) -> dmc.Stack:
        return dmc.Stack(
            [
                html.Span(t(upper), style={"font-size": 10, "color": "grey"}),
                html.Span(t(lower), style={"font-size": 12}),
            ],
            gap=0,
        )

    def __badge(
        self,
        event_type: LogType,
    ) -> dmc.TableTd:
        color = {
            LogType.DELETE: "red",
            LogType.INSERT: "green",
            LogType.UPDATE: "blue",
        }[event_type]

        return dmc.TableTd(dmc.Badge(event_type.value, color=color, variant="light"))

    def __time(self, event_time) -> dmc.TableTd:
        return dmc.TableTd(self.__text(event_time[:10], event_time[11:19]))

    def __user(self, event_user) -> dmc.TableTd:
        return dmc.TableTd(event_user)

    def __row_id(self, event_values: dict):
        row_id = event_values.get("row_id", None)
        return dmc.TableTd(row_id)

    def __values(self, values: dict, event_type: LogType) -> dmc.TableTd:
        match event_type:
            case LogType.UPDATE:
                children = dmc.Group(
                    [
                        html.B(f'{t(values["column_name"])}:'),
                        html.Span(t(values["old_value"])),
                        DashIconify(icon="mingcute:arrow-right-fill"),
                        html.Span(t(values["new_value"])),
                    ],
                    gap="xs",
                )

            case LogType.INSERT:
                values = [self.__text(key, values[key]) for key in values]
                children = dmc.Group(values)

        return dmc.TableTd(children)

    def __undo_button(self) -> dmc.TableTd:
        return dmc.TableTd(
            dmc.ActionIcon(
                DashIconify(icon="mingcute:back-2-fill", width=20),
                size="lg",
                color="red",
                radius="md",
            )
        )

    def render_event(self, event) -> dmc.Group:
        event_type = LogType(event[2])
        event_values = json.loads(event[7])

        data = [
            self.__badge(event_type),
            self.__user(event[6]),
            self.__time(event[1]),
            self.__row_id(event_values),
            self.__values(event_values, event_type),
            self.__undo_button(),
        ]

        return dmc.TableTr(data)

    @property
    def rows(self):
        history = get_history()
        return dmc.Table(
            [
                dmc.TableThead(
                    [
                        dmc.TableTr(
                            [
                                dmc.TableTh("Type"),
                                dmc.TableTh("User"),
                                dmc.TableTh("Time"),
                                dmc.TableTh("Row ID"),
                                dmc.TableTh("Values"),
                                dmc.TableTh("Undo"),
                            ]
                        )
                    ]
                ),
                dmc.TableTbody([self.render_event(event) for event in history]),
            ],
            striped=True,
            withRowBorders=False,
            withColumnBorders=False,
            stickyHeader=True,
        )
