import cx_Oracle
import os


def start_pool():
    pool_min = 0
    pool_max = 4
    pool_inc = 0
    pool_gmd = cx_Oracle.SPOOL_ATTRVAL_WAIT
    print("Connecting")
    cx_Oracle.init_oracle_client(lib_dir=os.environ.get('PATH_TO_INSTANTCLIENT'))
    db = cx_Oracle.SessionPool(user=os.environ.get('ORACLE_USER'),
                               password=os.environ.get('ORACLE_PASSWD'),
                               dsn='oracleclouddb_high',
                               min=pool_min,
                               max=pool_max,
                               increment=pool_inc,
                               threaded=True,
                               getmode=pool_gmd)

    return db


# def close_db():
#     db = g.pop('db', None)
#
#     if db is not None:
#         db.close()
