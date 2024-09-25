from time import time

from dash import no_update
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import sessionmaker

from ...history import LogType, post_history
from ...models import get_table_model
from ...utils import raise_error, split_pathname, config, db


class InsertRowCallback:
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
                post_history(
                    log_type=LogType.INSERT,
                    group_name=self.group_name,
                    table_name=self.banana_table.name,
                    schema_name=self.banana_table.schema_name,
                    user_name=config.connection.username,
                    log_data=self.values,
                )
                return False, int(time())

            except Exception as e:
                session.rollback()
                raise_error("Error inserting row", str(e.orig))
                return no_update, no_update

            finally:
                session.close()
