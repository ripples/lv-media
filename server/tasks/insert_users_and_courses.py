import csv
from collections import defaultdict
from os import listdir
from shutil import move
from os.path import isfile, join, splitext
from pathlib import Path

import xlrd

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

    users = set()
    courses = set()
    users_to_courses = defaultdict(list)

    for file_path in files:
        _, extension = splitext(file_path)

        if extension == '.csv':
            _read_csv(file_path, semester, users, courses, users_to_courses)
        elif extension == '.xls' or extension == '.xlsx':
            _read_excel(file_path, semester, users, courses, users_to_courses)
        _move_to_inserted_directory(file_path)
    _insert_data(users, courses, users_to_courses)


def _read_csv(file: str, semester: str, users: set, courses: set, users_to_courses: dict):
    """

    Reads Umass style csv format

    Args:
        :param (str) file: file to parse
        :param (str) semester: current semester
        :param (set) users: global store of users
        :param (set) courses: global store of courses
        :param (set) users_to_courses: global store users to courses mapping
    """

    with open(file, mode='r') as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')

        for row in reader:
            email = row[-1]
            users.add((email, None, None))

            course_parts = row[1].split()
            course_name = '{}{}'.format(course_parts[0], course_parts[1])
            course = (course_name, semester)
            courses.add(course)

            users_to_courses[email].append([course_name, semester])


def _read_excel(file: str, semester: str, users: set, courses: set, users_to_courses: dict):
    """

    Reads Ithaca style excel format

    Args:
        :param (str) file: file to parse
        :param (str) semester: current semester
        :param (set) users: global store of users
        :param (set) courses: global store of courses
        :param (set) users_to_courses: global store users to courses mapping
    """
    course_parts = file.split('/')[-1].split('_')
    course_name = '{}{}'.format(course_parts[0], course_parts[1])
    courses.add((course_name, semester))

    book = xlrd.open_workbook(file)
    sheet = book.sheet_by_index(0)
    skip = True

    for row in sheet.get_rows():
        first_column = row[0].value
        if skip:
            skip = not first_column.startswith("Name")
            continue
        elif first_column == "" or first_column is None:
            continue

        full_name = first_column
        name_parts = [name.strip() for name in full_name.split(', ')]

        email = row[1].value + '@ithaca.edu'
        users.add((email, name_parts[0], name_parts[1]))

        users_to_courses[email].append([course_name, semester])


def _insert_data(users: set, courses: set, users_to_courses: dict):
    """

    Inserts the emails, courses and user to courses mapping into db

    Args:
        :param (set) users: users to insert
        :param (set) courses: courses to insert
        :param (dict) users_to_courses: users to courses mapping to insert
    """
    connection = connect()
    with connection.cursor() as cursor:
        if len(users) > 0:
            cursor.executemany('''
                      INSERT IGNORE INTO users(email, fname, lname)
                      VALUES(%s, %s, %s)
                      ''', users)

        if len(courses) > 0:
            cursor.executemany('''
                      INSERT IGNORE INTO courses(id, semester_id)
                      VALUES(%s, %s)
                      ''', list(courses))

        if len(users) <= 0:
            return

        emails = list(map(lambda user: user[0], users))
        cursor.execute(
            bind_values(
                '''SELECT id, email
                   FROM users
                   WHERE email IN ({})''',
                emails),
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
