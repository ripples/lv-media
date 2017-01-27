import csv
from collections import defaultdict
from server.libs.database import connect_or_wait, get_current_semester


def run(file_path: str, db_credentials: dict) -> None:
    connection = connect_or_wait(db_credentials)

    with open(file_path, mode='r', newline='') as students:
        reader = csv.reader(students, delimiter=',', quotechar='"')
        courses_to_users = defaultdict(list)
        users = {}
        semester = get_current_semester()
        i = 1

        with connection.cursor() as cursor:
            # Super shitty but dirty way of checking if we've already inserted into db
            cursor.execute('SELECT * FROM users WHERE id = 1')
            if bool(cursor.fetchone()):
                return

            password = '$2a$10$JofcKIcaYmEaFudtzfuAfuFpwLPe3t/czs/cKdsz0IEdieXmWnu76'
            for row in reader:
                course_info = row[1].split()
                email = row[-1]
                course = '{} {}'.format(course_info[0], course_info[1])

                if email not in users:
                    users[email] = (i, password, email, '', '', '2', 0)
                    courses_to_users[course].append(i)
                    i += 1
                else:
                    courses_to_users[course].append(users[email][0])

            cursor.executemany('''
                  INSERT INTO users(id, password, email, fname, lname, user_type_id, verified)
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
