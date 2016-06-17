#! /usr/bin/env python3
import os
import sys
import json
from flask import Flask, abort
import media

# Initialize the media object to None. This gets
# created from the command line arguments.
mediaobj = None

# Create the Flask application
app = Flask(__name__)


@app.route('/favicon.ico')
def index():
    abort(404)


@app.route('/semesters')
def semesters():
    return json.dumps(mediaobj.semesters())


@app.route('/<semester>')
def courses(semester):
    return json.dumps(mediaobj.courses(semester))


@app.route('/<semester>/<course>')
def lectures(semester, course):
    return json.dumps(mediaobj.lectures(semester, course))


@app.route('/<semester>/<course>/<lecture>')
def lecture(semester, course, lecture):
    return json.dumps(mediaobj.lecture(semester, course, lecture))

if __name__ == '__main__':
    # TODO: use argparse
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print('usage: {} MEDIA_DIR DEBUG or create the appropriate system variable'.format(sys.argv[0]))
        sys.exit()
    elif 'MEDIA_DIR' in os.environ:
        media_dir = os.environ['MEDIA_DIR']
    else:
        media_dir = sys.argv[1]

    mediaobj = media.mock(media_dir)
    port = 5000
    if 'MEDIA_SERVER_PORT' in os.environ:
        port = int(os.environ['MEDIA_SERVER_PORT'])

    # TODO: use flag to define debug or not, we shouldn't have debug in prod
    app.run(host="0.0.0.0", port=port, debug=True)
