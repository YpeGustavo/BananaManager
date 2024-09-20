from typing import Literal

from dash_iconify import DashIconify
import dash_mantine_components as dmc

from ..log import read_history
from ..models import BananaTable, get_table_model
from ..utils import split_pathname


class LoadHistoryCallback:
    def __init__(self, pathname: str):
        group_name, table_name = split_pathname(pathname)
        banana_table = get_table_model(group_name, table_name)

    def __get_icon(
        self,
        event_type: Literal["DELETE", "INSERT", "UPDATE"],
    ) -> dmc.TableTd:
        color = {
            "DELETE": "red",
            "INSERT": "green",
            "UPDATE": "blue",
        }[event_type]

        return dmc.TableTd(dmc.Badge(event_type, color=color, variant="light"))

    def __get_id(self, event_id) -> dmc.TableTd:
        return dmc.TableTd(str(event_id))

    def __get_time(self, event_time) -> dmc.TableTd:
        return dmc.TableTd(event_time[:16])

    def __get_user(self, event_user) -> dmc.TableTd:
        return dmc.TableTd(event_user)

    def __get_undo_button(self) -> dmc.TableTd:
        return dmc.TableTd(
            dmc.ActionIcon(
                DashIconify(icon="mingcute:back-2-fill", width=20),
                size="lg",
                color="red",
                radius="md",
            )
        )

    def render_event(self, event) -> dmc.Group:
        data = [
            self.__get_icon(event[5]),
            self.__get_user(event[1]),
            self.__get_time(event[7]),
            self.__get_id(event[6]),
            dmc.TableTd("Placeholder"),
            self.__get_undo_button(),
        ]

        return dmc.TableTr(data)

    @property
    def rows(self):
        history = read_history()
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
