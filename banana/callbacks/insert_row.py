from json import dumps
from time import time

from dash import set_props, no_update
from dash_iconify import DashIconify
from dash_mantine_components import Notification
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import sessionmaker

from ..log import log_insert
from ..models import get_table_model
from ..utils import split_pathname, config, db


class InsertRow:
    def __init__(self, pathname, fields):
        self.group_name, table_name = split_pathname(pathname)
        self.banana_table = get_table_model(self.group_name, table_name)
        self.values = self.get_values(fields)
        self.metadata = MetaData()
        self.table = None
        self.Session = sessionmaker(bind=db.engine)

    def get_values(self, fields):
        return {
            field["id"]["column"]: field["value"] for field in fields if field["value"]
        }

    def reflect_table(self):
        try:
            self.table = Table(
                self.banana_table.name,
                self.metadata,
                schema=self.banana_table.schema_name,
                autoload_with=db.engine,
            )
        except Exception as e:
            print(f"Error reflecting table: {e}")

    def exec(self):
        self.reflect_table()
        if self.table is not None:
            query = self.table.insert().values(**self.values)
            session = self.Session()
            try:
                session.execute(query)
                session.commit()
                log_insert(
                    user_name=config.connection.username,
                    group_name=self.group_name,
                    table_name=self.banana_table.name,
                    schema_name=self.banana_table.schema_name,
                    new_values=dumps(self.values),
                )
                return False, int(time())

            except Exception as e:
                session.rollback()
                notify = Notification(
                    title="Error inserting row",
                    action="show",
                    message=str(e.orig),
                    icon=DashIconify(icon="maki:cross"),
                    color="red",
                    autoClose=False,
                    withBorder=True,
                    radius="md",
                )
                set_props("banana--notification", {"children": notify})
                return no_update, no_update

            finally:
                session.close()
