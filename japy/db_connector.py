from functools import wraps
from os import environ
import psycopg2 as db


def cursor(func):
    connection_string = f"host={environ['DB_HOST']} user={environ['DB_USER']} password={environ['DB_PASSWORD']} dbname={environ['DB_DBNAME']}"

    @wraps(func)
    def wrapper(*args, **kwargs):
        connection = db.connect(connection_string)
        _cursor = connection.cursor()
        try:
            value = func(_cursor, *args, **kwargs)
            connection.commit()
            return value
        except Exception:
            connection.rollback()
            raise

    return wrapper
