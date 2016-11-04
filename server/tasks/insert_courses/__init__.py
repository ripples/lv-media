import itertools
from server.libs.database import connect_or_wait, get_current_semester


def run(cache: dict, db_credentials: dict):
    connection = connect_or_wait(db_credentials)
    semester = get_current_semester()
    with connection as cursor:
        cached_courses = list(cache[semester].keys())
        cursor.execute('SELECT id FROM courses WHERE semester_id = %s', args=[semester])
        db_courses = list(itertools.chain(*cursor.fetchall()))

        courses_to_insert = [(course_id, "", semester) for course_id in cached_courses if course_id not in db_courses]
        cursor.executemany('INSERT INTO courses(id, name, semester_id) VALUES(%s, %s, %s)', courses_to_insert)
