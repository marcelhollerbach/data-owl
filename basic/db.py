import sqlite3
from sqlite3 import Connection

from flask import g

DATABASE = './test_db.db'


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_db_connection() -> Connection:
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
