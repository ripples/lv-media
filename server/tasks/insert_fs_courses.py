import logging

from server.libs.database import connect, get_latest_semester


def run(cache: dict):
    connection = connect()
    semester = get_latest_semester()

    try:
        cached_courses = list(cache[semester].keys())
    except KeyError as e:
        logging.getLogger().error('HOST_MEDIA_DIR does not contain the directory {}'.format(semester))
        raise e

    with connection.cursor() as cursor:
        courses_to_insert = [(course_id, semester) for course_id in cached_courses]
        cursor.executemany('''
                  INSERT IGNORE INTO courses(id, semester_id)
                  VALUES(%s, %s)
                  ''', courses_to_insert)

