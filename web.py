#! /usr/bin/env python3
import argparse
import os
import sys
import json
from flask import Flask, abort
import media

# Initialize the media object to None. This gets
# created from the command line arguments.
media_parser = None

# Create the Flask application
app = Flask(__name__)


@app.route('/favicon.ico')
def index():
    abort(404)


@app.route('/semesters')
def semesters():
    return json.dumps(media_parser.semesters())


@app.route('/<semester>')
def courses(semester):
    return json.dumps(media_parser.courses(semester))


@app.route('/<semester>/<course>')
def lectures(semester, course):
    return json.dumps(media_parser.lectures(semester, course))


@app.route('/<semester>/<course>/<lecture>')
def lecture_metadata(semester, course, lecture):
    return json.dumps(media_parser.lecture_metadata(semester, course, lecture))


@app.route('/<semester>/<course>/<lecture>/media')
def lecture_media_data(semester, course, lecture):
    return json.dumps(media_parser.lecture_media_data(semester, course, lecture))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='set MEDIA_DIR in environment variable or provide a media directory')

    parser.add_argument('-m', '--media_dir', metavar='DIRECTORY', type=str, help='media directory')
    parser.add_argument('-d', '--debug', action='store_true', help='enable flask debugging')
    args = parser.parse_args()

    if args.media_dir:
        media_dir = args.media_dir
    elif 'MEDIA_DIR' in os.environ:
        media_dir = args.media_dir
    else:
        parser.print_help()
        sys.exit()

    media_parser = media.ActualMedia(media_dir)

    app.run(host="0.0.0.0", port=5000, debug=(bool(args.debug)))
