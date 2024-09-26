from dash import set_props
from dash_mantine_components import Notification


def raise_error(title: str, message):
    notify = Notification(
        title=title,
        action="show",
        message=message,
        color="red",
        autoClose=False,
        withBorder=True,
        radius="md",
    )
    set_props("banana--notification", {"children": notify})


def split_pathname(pathname: str) -> tuple[str]:
    try:
        _, group_name, table_name = pathname.split("/")
    except ValueError:
        group_name = None
        table_name = None
    return group_name, table_name
