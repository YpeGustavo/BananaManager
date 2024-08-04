from dash import dcc, html
from dash_ag_grid import AgGrid
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from .utils import config


class Layout(dmc.MantineProvider):
    def __init__(self):
        super().__init__(
            html.Div(
                [
                    dcc.Location(id="banana--location", refresh=False),
                    self.add_modal(),
                    self.left_section(),
                    self.right_section(),
                ],
                className="container",
            )
        )

    def left_section(self) -> html.Div:
        return dmc.Paper(
            id="banana--menu",
            className="left-section",
            bg=dmc.DEFAULT_THEME["colors"][config.theme][9],
        )

    def right_section(self) -> html.Div:
        return html.Div(
            html.Div(
                [
                    self.right_section_header(),
                    AgGrid(
                        id="banana--table",
                        dashGridOptions=config.grid_options,
                        style={
                            "height": "calc(100vh - 85px)",
                            "overflow": "auto",
                        },
                    ),
                ],
                className="content",
            ),
            className="right-section",
        )

    def right_section_header(self) -> dmc.Group:
        return dmc.Group(
            [
                dmc.Text(
                    id="banana--table-title",
                    className="table-title",
                    c=dmc.DEFAULT_THEME["colors"][config.theme][9],
                ),
                dmc.Group(
                    [
                        dmc.Button(
                            "Add row",
                            id="banana--add-button",
                            color="green",
                            radius="md",
                            leftSection=DashIconify(
                                icon="mingcute:add-circle-fill", height=20
                            ),
                        ),
                        dmc.Button(
                            "Refresh",
                            id="banana--refresh-button",
                            color=config.theme,
                            radius="md",
                            leftSection=DashIconify(
                                icon="mingcute:refresh-3-fill", height=20
                            ),
                        ),
                    ]
                ),
            ],
            justify="space-between",
        )

    def add_modal(self) -> dmc.Modal:
        return dmc.Modal(
            [
                dmc.SimpleGrid(id="banana--add-form", cols=2),
                dmc.Center(
                    [
                        dmc.Button(
                            "Cancel",
                            id="banana--add-cancel",
                            color="red",
                            radius="md",
                            variant="subtle",
                            leftSection=DashIconify(
                                icon="mingcute:close-circle-fill",
                                height=20,
                            ),
                            mr=10,
                        ),
                        dmc.Button(
                            "Confirm",
                            id="banana--add-confirm",
                            color="green",
                            radius="md",
                            leftSection=DashIconify(
                                icon="mingcute:add-circle-fill",
                                height=20,
                            ),
                        ),
                    ],
                    mt=20,
                ),
            ],
            id="banana--add-modal",
            opened=False,
        )
