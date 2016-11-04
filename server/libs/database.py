from time import sleep
import pymysql
from datetime import datetime

_connection = None
# id, start epoch, end epoch
_current_semester = ("", 0, 0)


def connect_or_wait(db_credentials: dict):
    global _connection
    if _connection:
        return _connection

    attempts = 0
    max_attempts = 10
    sleep_time = 3

    while not _connection:
        try:
            _connection = pymysql.connect(**db_credentials)
        except pymysql.err.OperationalError:
            if attempts >= max_attempts:
                print('Failed to connect to db after {} seconds'.format(sleep_time * max_attempts))
                raise pymysql.err.OperationalError()
            print('Could not connect to db, sleeping for {}s'.format(sleep_time))
            attempts += 1
            sleep(sleep_time)
    return _connection


def get_current_semester():
    global _current_semester

    with _connection as cursor:
        if datetime.utcnow().timestamp() > _current_semester[2]:
            cursor.execute("""SELECT id, UNIX_TIMESTAMP(start_dtm), UNIX_TIMESTAMP(end_dtm)
                              FROM semesters ORDER BY end_dtm DESC LIMIT 1""")
            _current_semester = cursor.fetchone()

    return _current_semester[0]
