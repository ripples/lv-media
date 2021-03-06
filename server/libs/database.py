import os
from datetime import datetime
from time import sleep

from typing import Union

import logging
import pymysql
from pymysql.connections import Connection

_connection = None
# id, start epoch, end epoch
_current_semester = ("", 0, 0)

db_credentials = {
    'password': os.environ['MYSQL_ROOT_PASSWORD'],
    'db': os.environ['MYSQL_DATABASE'],
    'host': os.environ['MYSQL_HOSTNAME'],
    'user': os.environ['MYSQL_USER']
}


def connect() -> Connection:
    """

    Connects to the database or uses existing connection

    Returns:
        Connection: database connection

    TODO:
        use DictCursor as default
    """
    global _connection
    if _connection:
        _connection.ping()
    else:
        _connection = pymysql.connect(**db_credentials, connect_timeout=60, autocommit=True)
    return _connection


def connect_or_wait() -> Connection:
    """

    Connects or waits to connect to the database or uses existing connection

    Returns:
        Connection: database connection

    TODO:
        use DictCursor as default
    """
    global _connection
    if _connection:
        _connection.ping()
        return _connection

    attempts = 0
    max_attempts = 10
    sleep_time = 3

    while not _connection:
        try:
            _connection = connect()
        except pymysql.err.OperationalError:
            if attempts >= max_attempts:
                logging.getLogger().error('Failed to connect to db after {} seconds'.format(sleep_time * max_attempts))
                raise pymysql.err.OperationalError()
            attempts += 1
            sleep(sleep_time)
    return _connection


def get_latest_semester() -> str:
    """

    Fetches the latest semester from the database

    Returns:
        str: The latest semester

    TODO:
        * Use current semester instead of latest once we figure out how to deal with semesters
    """
    global _current_semester

    with _connection as cursor:
        if datetime.utcnow().timestamp() > _current_semester[2]:
            cursor.execute("""SELECT id, UNIX_TIMESTAMP(start_dtm), UNIX_TIMESTAMP(end_dtm)
                              FROM semesters ORDER BY end_dtm DESC LIMIT 1""")
            _current_semester = cursor.fetchone()

    return _current_semester[0]


def bind_values(query: str, args: Union[list, set]) -> str:
    """

    Formats a query that has a single '{}' with the proper amount of '%s' based on args size

    Args:
        :param (str) query: query to format
        :param (Union[list, set]) args: list of args

    Returns:
        str: Formatted query
    """

    return query.format(', '.join(list(map(lambda x: '%s', args))))
