from dash import set_props
from dash_mantine_components import Notification
import yaml


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


def read_yaml(file) -> dict:
    try:
        with open(file, "r", encoding="utf8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise Exception(f"Config file `{file}` not found.")
    except yaml.YAMLError as exc:
        raise Exception(f"Error parsing YAML config file: {exc}")


def split_pathname(pathname: str) -> tuple[str]:
    try:
        _, group_name, table_name = pathname.split("/")
    except ValueError:
        group_name = None
        table_name = None
    return group_name, table_name
