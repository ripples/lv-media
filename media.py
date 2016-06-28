import re
from os import listdir
from os.path import isfile, isdir, join


class MockMedia:
    def __init__(self, location):
        self.location = location

    def semesters(self):
        return ['F13', 'F14', 'F15', 'S14', 'S15', 'S16']

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
                'computer1456855479-0-thumb.png',
                'computer1456855749-0.png',
                'computer1456855749-0-thumb.png'
            ],
            'whiteboard': [
                'whiteBoard1456854911-0.png',
                'whiteBoard1456854911-0-thumb.png',
                'whiteBoard1456854912-0.png',
                'whiteBoard1456854912-0-thumb.png',
                'whiteBoard1456854913-0.png'
                'whiteBoard1456854913-0-thumb.png'
            ]
        }


class ActualMedia:
    def __init__(self, location):
        self.location = location

    def semesters(self):
        return [d for d in listdir(self.location) if isdir(join(self.location, d))]

    def courses(self, semester):
        dir = join(self.location, semester)
        return [d for d in listdir(dir) if isdir(join(dir, d))]

    def lectures(self, semester, course):
        dir = join(self.location, semester, course)
        return [d for d in listdir(dir) if isdir(join(dir, d))]

    def _read_info(self, infofile):
        data = {}
        with open(infofile) as info:
            for line in info.readlines():
                m = re.search('duration: (\d+)', line)
                if m != None:
                    data['duration'] = m.group(1)

                m = re.search('timestamp: (\d+)', line)
                if m != None:
                    data['timestamp'] = m.group(1)

                m = re.search('source: (.+)', line)
                if m != None:
                    data['source'] = m.group(1)

                m = re.search('whiteboardCount: (.+)', line)
                if m != None:
                    data['whiteboard_count'] = m.group(1)

                m = re.search('computerCount: (.+)', line)
                if m != None:
                    data['computer_count'] = m.group(1)

        return data

    def lecture(self, semester, course, lecture):
        lecturedir = join(self.location, semester, course, lecture)
        infofile   = join(lecturedir, 'INFO')
        data       = self._read_info(infofile)
        cdir       = join(lecturedir, 'computer')
        ldir       = join(lecturedir, 'whiteboard')
        data['computer']   = [f for f in listdir(cdir) if isfile(join(cdir, f))]
        data['whiteboard'] = [f for f in listdir(ldir) if isfile(join(ldir, f))]
        data['semester']   = semester
        data['course']     = course
        data['lecture']    = lecture
        data['curl']       = join('media', semester, course, lecture, 'computer')
        data['wurl']       = join('media', semester, course, lecture, 'whiteboard')
        return data


def mock(location):
    return MockMedia(location)


def make(location):
    return ActualMedia(location)
