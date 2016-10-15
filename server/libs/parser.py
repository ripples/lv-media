import re
from os import listdir, environ
from os.path import isdir, join


class Parser:
    def __init__(self, location=environ.get('IMAGE_MEDIA_DIR')):
        self.location = location

    def semesters(self) -> list:
        return [d for d in listdir(self.location) if isdir(join(self.location, d))]

    def courses(self, semester: str) -> list:
        dir = join(self.location, semester)
        return [d for d in listdir(dir) if isdir(join(dir, d))]

    def lectures(self, semester: str, course: str) -> list:
        dir = join(self.location, semester, course)
        return [d for d in listdir(dir) if isdir(join(dir, d))]

    def lecture_meta(self, semester: str, course: str, lecture: str) -> dict:
        lecture_dir = join(self.location, semester, course, lecture)
        info_file = join(lecture_dir, 'INFO')
        return self._read_info(info_file)

    def lecture_data(self, semester: str, course: str, lecture: str) -> dict:
        lecture_dir = join(self.location, semester, course, lecture)
        whiteboard_directory = join(lecture_dir, 'whiteboard')
        computer_directory = join(lecture_dir, 'computer')

        return {
            'whiteboard': self._read_image_files(whiteboard_directory),
            'computer': self._read_image_files(computer_directory)
        }

    def read_all(self):
        return {semester:
                {course:
                 {lecture:
                  {k_meta: v_meta
                   for k_meta, v_meta in self.lecture_meta(semester, course, lecture).items()}
                  for lecture in self.lectures(semester, course)}
                 for course in self.courses(semester)}
                for semester in self.semesters()}

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
                    data['timestamp'] = int(match.group(1))

                match = re.search('source: (.+)', line)
                if match is not None:
                    data['source'] = match.group(1)

        return data

    @staticmethod
    def _read_image_files(directory: str) -> dict:
        files = {}
        for current_file in listdir(directory):
            if not current_file.endswith('-thumb.png'):
                file_name = current_file.split('.')[0]
                file_info = file_name.split('-')
                id = file_info[1]
                if id not in files:
                    files[id] = []
                files.get(id).append(file_name)

        return {id: sorted(file_list, key=lambda file: file) for id, file_list in files.items()}
