from .instances import db


def read_sql(query):
    with db.engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()
    return rows
