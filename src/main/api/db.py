import os
from dotenv import load_dotenv

import psycopg

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

_conn = None


def get_conn():
    global _conn

    if _conn is None or _conn.closed:
        _conn = psycopg.connect(DATABASE_URL)

    return _conn