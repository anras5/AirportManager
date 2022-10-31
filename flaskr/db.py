import cx_Oracle
from flask import g
import os


def get_db():
    if 'db' not in g:
        try:
            cx_Oracle.init_oracle_client(lib_dir=os.environ.get('PATH_TO_INSTANTCLIENT'))
        except:
            pass
        g.db = cx_Oracle.connect(user=os.environ.get('ORACLE_USER'),
                                 password=os.environ.get('ORACLE_PASSWD'),
                                 dsn='oracleclouddb_high')

    return g.db


def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()
