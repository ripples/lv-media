import re
from os import listdir
from os.path import isfile, isdir, join


class MockMedia:
    def __init__(self, location):
        self.location = location

    def semesters(self):
        return ['F13', 'F14', 'F15', 'S14', 'S15', 'S16', 'F16']

    def courses(self, semester):
        return [
            'COMPSCI590C',
            'COMPSCI677',
            'COMPSCI683',
            'COMPSCI690P'
        ]

    def lectures(self, semester, course):
        return [
            '03-01-2016--12-55-02',
            '03-08-2016--12-55-01'
        ]

    def lecture(self, semester, course, lecture):
        return {
            'timestamp': 1456854902,
            'duration': 5100,
            'source': 'cap142',
            'whiteboard_count': 1,
            'computer_count': 1,
            'computer': [
                'computer1456855479-0.png',
                'computer1456855749-0.png'
            ],
            'whiteboard': [
                'whiteBoard1456854911-0.png',
                'whiteBoard1456854912-0.png',
                'whiteBoard1456854913-0.png'
            ]
        }


class ActualMedia:
    def __init__(self, location: str):
        self.location = location

    def semesters(self) -> list:
        return [d for d in listdir(self.location) if isdir(join(self.location, d))]

    def courses(self, semester: str) -> list:
        dir = join(self.location, semester)
        return [d for d in listdir(dir) if isdir(join(dir, d))]

    def lectures(self, semester: str, course: str) -> list:
        dir = join(self.location, semester, course)
        return [d for d in listdir(dir) if isdir(join(dir, d))]

    @staticmethod
    def _read_info(info_file: str) -> dict:
        data = {}
        with open(info_file) as info:
            for line in info.readlines():
                match = re.search('duration: (\d+)', line)
                if match is not None:
                    data['duration'] = match.group(1)

                match = re.search('timestamp: (\d+)', line)
                if match is not None:
                    data['timestamp'] = match.group(1)

                match = re.search('source: (.+)', line)
                if match is not None:
                    data['source'] = match.group(1)

                match = re.search('whiteboardCount: (.+)', line)
                if match is not None:
                    data['whiteboard_count'] = match.group(1)

                match = re.search('computerCount: (.+)', line)
                if match is not None:
                    data['computer_count'] = match.group(1)

        return data

    def lecture(self, semester: str, course: str, lecture: str) -> dict:
        lecture_dir = join(self.location, semester, course, lecture)
        info_file = join(lecture_dir, 'INFO')
        data = self._read_info(info_file)
        cdir = join(lecture_dir, 'computer')
        ldir = join(lecture_dir, 'whiteboard')
        data['computer'] = [f for f in listdir(cdir) if isfile(join(cdir, f))]
        data['whiteboard'] = [f for f in listdir(ldir) if isfile(join(ldir, f))]
        data['semester'] = semester
        data['course'] = course
        data['lecture'] = lecture
        data['curl'] = join('media', semester, course, lecture, 'computer')
        data['wurl'] = join('media', semester, course, lecture, 'whiteboard')
        return data


def mock(location: str) -> MockMedia:
    return MockMedia(location)


def make(location: str) -> ActualMedia:
    return ActualMedia(location)
