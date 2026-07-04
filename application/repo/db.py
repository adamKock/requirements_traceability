
import os
import psycopg2
from psycopg2.pool import ThreadedConnectionPool



DB_POOL = ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)


def get_connection():
    return ThreadedConnectionPool.connect(
         minconn=1,
        maxconn=10,
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

def get_db_connection():
    """Context manager to handle automated checkout and return of connections."""
    conn = DB_POOL.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        DB_POOL.putconn(conn)