from datetime import datetime
import enum
import json
from typing import Optional

from pydantic import validate_call
from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    Integer,
    String,
    DateTime,
    and_,
    create_engine,
    select,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .utils import config


Base = declarative_base()


class LogType(enum.Enum):
    DELETE = "DELETE"
    INSERT = "INSERT"
    UPDATE = "UPDATE"


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_time = Column(DateTime, default=datetime.now)
    log_type = Column(Enum(LogType))
    group_name = Column(String)
    table_name = Column(String)
    schema_name = Column(String)
    user_name = Column(String)
    log_data = Column(String)
    undone = Column(Boolean, default=False)


db_dir = config.dataPath.joinpath("history.db")
engine = create_engine(f"sqlite:///{db_dir}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@validate_call
def get_history(group_name: str, table_name: str, schema_name: Optional[str]):
    query = (
        select(
            History.log_type,
            History.user_name,
            History.log_time,
            History.log_data,
        )
        .where(
            and_(
                History.group_name == group_name,
                History.table_name == table_name,
                History.undone == 0,
            )
        )
        .order_by(History.id.desc())
    )

    if schema_name is not None:
        query = query.where(History.schema_name == schema_name)
    else:
        query = query.where(History.schema_name.is_(None))

    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()

    return rows


@validate_call
def post_history(
    log_type: LogType,
    group_name: str,
    table_name: str,
    schema_name: Optional[str],
    user_name: str,
    log_data: dict,
) -> int | None:

    session = Session()
    try:
        values = History(
            log_type=log_type.value,
            group_name=group_name,
            table_name=table_name,
            schema_name=schema_name,
            user_name=user_name,
            log_data=json.dumps(log_data),
        )
        session.add(values)
        session.commit()
        return values.id
    except Exception as e:
        print(f"Session rollback because of exception: {e}")
        session.rollback()
    finally:
        session.close()
