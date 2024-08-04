from sqlalchemy import MetaData, Table
from sqlalchemy.orm import sessionmaker

from ..models import get_table_model
from ..utils import split_pathname, db


class InsertRow:
    def __init__(self, pathname, fields):
        group, table = split_pathname(pathname)
        self.banana_table = get_table_model(table, group)
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

    def insert(self):
        self.reflect_table()
        if self.table is not None:
            query = self.table.insert().values(**self.values)
            session = self.Session()
            try:
                session.execute(query)
                session.commit()
                print(f"Inserted values: {self.values}")
            except Exception as e:
                session.rollback()
                print(f"Error inserting row: {e}")
            finally:
                session.close()
