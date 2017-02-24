import csv
from collections import defaultdict
from os import listdir
from shutil import move
from os.path import isfile, join, splitext
from pathlib import Path

from server import CONTAINER_MEDIA_DIR
from server.libs.database import connect, get_latest_semester, bind_values


def run():
    """

    Inserts users and their associated courses into the database from supported files found in the users directory.
    Those files are then moved into the users/inserted directory

    Note:
        Currently supported files include, update if you add support for another file type:
            * csv: Umass style
    """
    users_dir = str(Path(CONTAINER_MEDIA_DIR, 'users'))
    semester = get_latest_semester()

    files = [join(users_dir, f) for f in listdir(users_dir) if isfile(join(users_dir, f))]

    emails = set()
    courses = set()
    users_to_courses = defaultdict(list)

    for file_path in files:
        _, extension = splitext(file_path)

        if extension == '.csv':
            _read_csv(file_path, semester, emails, courses, users_to_courses)
        _move_to_inserted_directory(file_path)
    _insert_data(emails, courses, users_to_courses)


def _read_csv(file: str, semester: str, emails: set, courses: set, users_to_courses: dict):
    """

    Reads Umass style csv format

    Args:
        :param (str) file: file to parse
        :param (str) semester: current semester
        :param (set) emails: global store of emails
        :param (set) courses: global store of courses
        :param (set) users_to_courses: global store users to courses mapping
    """

    with open(file, mode='r') as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')

        for row in reader:
            email = row[-1]
            if email not in emails:
                emails.add(email)

            course_info = row[1].split()
            course_name = '{} {}'.format(course_info[0], course_info[1])
            course = (course_name, semester)

            if course not in courses:
                courses.add(course)

            users_to_courses[email].append([course_name, semester])


def _insert_data(emails: set, courses: set, users_to_courses: dict):
    """

    Inserts the emails, courses and user to courses mapping into db

    Args:
        :param (set) emails: emails to insert
        :param (set) courses: courses to insert
        :param (dict) users_to_courses: users to courses mapping to insert
    """
    connection = connect()
    with connection.cursor() as cursor:
        if len(emails) > 0:
            cursor.executemany('''
                      INSERT IGNORE INTO users(email)
                      VALUES(%s)
                      ''', emails)

        if len(courses) > 0:
            cursor.executemany('''
                      INSERT IGNORE INTO courses(id, semester_id)
                      VALUES(%s, %s)
                      ''', list(courses))

        if len(emails) <= 0:
            return

        cursor.execute(
            bind_values('''SELECT id, email
                           FROM users
                           WHERE email IN %s''', emails),
            emails)
        lkp_course_users = []
        user_rows = cursor.fetchall()
        for user_row in user_rows:
            user_courses = users_to_courses[user_row[1]]
            for user_course in user_courses:
                user_course.append(user_row[0])
                lkp_course_users.append(user_course)

        if len(lkp_course_users) > 0:
            cursor.executemany('''
                      INSERT IGNORE INTO lkp_course_users(course_id, semester_id, user_id)
                      VALUES (%s, %s, %s)
                      ''', lkp_course_users)


def _move_to_inserted_directory(file_path: str):
    """

    Moves file to the inserted directory

    /media/users/file -> /media/users/inserted/file

    Args:
        :param (str) file_path: absolute file path
    """
    parts = list(Path(file_path).parts)
    parts.insert(-1, 'inserted')
    move(file_path, str(Path(*parts)))
