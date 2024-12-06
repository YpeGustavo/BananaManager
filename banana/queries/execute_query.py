from sqlalchemy.orm import sessionmaker, scoped_session

from ..core.instances import db
from ..core.utils import raise_error


def exec_sql(query) -> None:
    session_factory = sessionmaker(bind=db.engine)
    Session = scoped_session(session_factory)
    session = Session()

    try:
        session.execute(query)
        session.commit()

    except Exception as err:
        session.rollback()
        raise err

    finally:
        session.close()
        Session.remove()


def read_sql(query):
    with db.engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()
    return rows
