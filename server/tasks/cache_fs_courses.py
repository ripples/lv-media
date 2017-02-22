from server.libs.parser import Parser


def run(courses: dict):
    parser = Parser()
    courses.update(parser.read_all())
