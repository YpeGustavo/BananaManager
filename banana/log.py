from datetime import datetime
import enum

from sqlalchemy import create_engine, Boolean, Column, Enum, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .utils import config


Base = declarative_base()


class LogType(enum.Enum):
    DELETE = "delete"
    INSERT = "insert"
    UPDATE = "update"


class Index(Base):
    __tablename__ = "log_index"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String)
    group_name = Column(String)
    table_name = Column(String)
    schema_name = Column(String)
    log_type = Column(Enum(LogType))
    log_index = Column(Integer)
    log_time = Column(DateTime, default=datetime.now)
    undone = Column(Boolean, default=False)


class Insert(Base):
    __tablename__ = "log_insert"
    id = Column(Integer, primary_key=True, autoincrement=True)
    new_values = Column(String)


class Update(Base):
    __tablename__ = "log_update"
    id = Column(Integer, primary_key=True, autoincrement=True)
    column_name = Column(String)
    row_id = Column(Integer)
    old_value = Column(String)
    new_value = Column(String)


db_dir = config.data_path.joinpath("log.db")
engine = create_engine(f"sqlite:///{db_dir}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def _log(base_class, **kwargs) -> int:
    session = Session()
    try:
        values = base_class(**kwargs)
        session.add(values)
        session.commit()
        return values.id
    except Exception as e:
        print(f"Session rollback because of exception: {e}")
        session.rollback()
    finally:
        session.close()


def log_insert(user_name, group_name, table_name, schema_name, new_values) -> None:
    update_id = _log(Insert, new_values=new_values)
    _log(
        Index,
        user_name=user_name,
        group_name=group_name,
        table_name=table_name,
        schema_name=schema_name,
        log_type=LogType.UPDATE,
        log_index=update_id,
    )


def log_update(
    user_name,
    group_name,
    table_name,
    schema_name,
    column_name,
    row_id,
    old_value,
    new_value,
) -> None:
    update_id = _log(
        Update,
        column_name=column_name,
        row_id=row_id,
        old_value=old_value,
        new_value=new_value,
    )

    _log(
        Index,
        user_name=user_name,
        group_name=group_name,
        table_name=table_name,
        schema_name=schema_name,
        log_type=LogType.UPDATE,
        log_index=update_id,
    )
