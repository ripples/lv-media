import csv
from collections import defaultdict
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry

from server.libs.database import connect_or_wait, get_current_semester


def run(file_path: str, envs: dict) -> None:
    connection = connect_or_wait(envs['db_credentials'])
    users = {}

    if envs['environment'] == "development":
        password = '$2a$10$JofcKIcaYmEaFudtzfuAfuFpwLPe3t/czs/cKdsz0IEdieXmWnu76'
        invite = False
    else:
        password = ''
        invite = True

    with open(file_path, mode='r', newline='') as students:
        reader = csv.reader(students, delimiter=',', quotechar='"')
        courses_to_users = defaultdict(list)
        semester = get_current_semester()
        i = 1

        with connection.cursor() as cursor:
            # Super shitty but dirty way of checking if we've already inserted into db
            cursor.execute('SELECT * FROM users WHERE id = 1')
            if bool(cursor.fetchone()):
                return

            for row in reader:
                course_info = row[1].split()
                email = row[-1]
                course = '{} {}'.format(course_info[0], course_info[1])

                if email not in users:
                    users[email] = (i, password, email, '', '', '2', 1)
                    courses_to_users[course].append(i)
                    i += 1
                else:
                    courses_to_users[course].append(users[email][0])

            cursor.executemany('''
                  INSERT INTO users(id, password, email, fname, lname, user_type_id, password_reset_required)
                  VALUES(%s, %s ,%s ,%s ,%s ,%s ,%s)
                  ''', users.values())

            courses = []
            lkp_course_users = []
            for course, ids in courses_to_users.items():
                courses.append((course, '', semester))
                for user_id in ids:
                    lkp_course_users.append((course, semester, user_id))

            cursor.executemany('''
                  INSERT INTO courses(id, name, semester_id)
                  VALUES(%s, %s, %s)
                  ''', courses)

            cursor.executemany('''
                  INSERT INTO lkp_course_users(course_id, semester_id, user_id)
                  VALUES(%s, %s, %s)
                  ''', lkp_course_users)
    connection.commit()

    if invite:
        url = 'http://{}:{}/internal/users/invite'.format(envs['lv-server-host'], envs['lv-server-port'])
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=Retry(total=10, backoff_factor=0.1)))
        s.post(url, json={'emails': list(users)})
