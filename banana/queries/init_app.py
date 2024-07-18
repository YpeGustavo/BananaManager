from sqlalchemy import Column, Integer, MetaData, String, Table, inspect, select, func
from sqlalchemy.orm import declarative_base, sessionmaker

from ..errors import InvalidBananaForeignKey, MultipleBananaTablesWithSameName
from ..models import BananaTables, BananaTable
from ..utils import read_sql, read_yaml, config, db


class InitApp:
    def check_foreign_key_uniqueness(self, table: BananaTable) -> bool:
        metadata = MetaData()

        for column in table.columns:
            if column.foreign_key is not None:
                foreign_table = Table(
                    column.foreign_key.table_name,
                    metadata,
                    schema=column.foreign_key.schema_name,
                    autoload_with=db.engine,
                )

                query = select(
                    (
                        func.count("*")
                        == func.count(
                            func.distinct(
                                foreign_table.c[column.foreign_key.column_name]
                            )
                        )
                    ),
                    (
                        func.count("*")
                        == func.count(
                            func.distinct(
                                foreign_table.c[column.foreign_key.column_display]
                            )
                        )
                    ),
                )

                rows = read_sql(query)

                if not rows[0][0]:
                    raise InvalidBananaForeignKey(
                        foreign_table.name,
                        column.foreign_key.column_name,
                    )
                elif not rows[0][1]:
                    raise InvalidBananaForeignKey(
                        foreign_table.name,
                        column.foreign_key.column_display,
                    )

    def read_values(self):
        values = list()
        unique_names = list()

        for table_path in config.table_paths:
            for suffix in ("*.yaml", "*.yml"):
                for file in table_path.rglob(suffix):
                    data = read_yaml(file)
                    tables = BananaTables(**data)
                    for table in tables.tables:
                        if table.name in unique_names:
                            raise MultipleBananaTablesWithSameName(table.name)
                        else:
                            self.check_foreign_key_uniqueness(table)
                            unique_names.append(table.name)
                            values.append(
                                {
                                    "schema_name": table.schema_name,
                                    "table_name": table.name,
                                    "table_display_name": table.display_name,
                                    "group_name": file.stem,
                                    "group_display_name": tables.group_name,
                                    "group_display_order": tables.display_order,
                                    "config_path": str(file),
                                }
                            )

        return values

    def index_tables(self):
        values = self.read_values()

        # Meta stuff
        Base = declarative_base()
        metadata = MetaData(schema=config.indexing_schema)
        metadata.bind = db.engine

        # Table structure
        class Indexing(Base):
            __tablename__ = config.indexing_table
            __table_args__ = {"schema": config.indexing_schema}
            id = Column(Integer, primary_key=True, autoincrement=True)
            schema_name = Column(String(255), nullable=True)
            table_name = Column(String(255), nullable=False)
            table_display_name = Column(String(255), nullable=True)
            group_name = Column(String(255), nullable=False)
            group_display_name = Column(String(255), nullable=True)
            group_display_order = Column(String(255), nullable=True)
            config_path = Column(String(255), nullable=False)

        # Create or replace table
        if inspect(db.engine).has_table(config.indexing_table, config.indexing_schema):
            Indexing.__table__.drop(db.engine)
        Base.metadata.create_all(db.engine)

        # Start session
        Session = sessionmaker(bind=db.engine)
        session = Session()

        # Insert values
        for value in values:
            new_record = Indexing(
                schema_name=value["schema_name"],
                table_name=value["table_name"],
                table_display_name=value["table_display_name"],
                group_name=value["group_name"],
                group_display_name=value["group_display_name"],
                group_display_order=value["group_display_order"],
                config_path=value["config_path"],
            )
            session.add(new_record)

        # Commit and close session
        session.commit()
        session.close()

    def refresh(self):
        self.index_tables()
