#! /usr/bin/env python3
import argparse
import os
import sys
import json
from flask import Flask, abort, jsonify, make_response
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
    try:
        return jsonify(media_parser.semesters())
    except OSError:
        return make_response(jsonify({"error": "Unable to read media directory"}), 404)


@app.route('/<semester>')
def courses(semester):
    try:
        return jsonify(media_parser.courses(semester))
    except OSError:
        return make_response(jsonify({"error": "Unable to read semester directory"}), 404)


@app.route('/<semester>/<course>')
def lectures(semester, course):
    try:
        return jsonify(media_parser.lectures(semester, course))
    except OSError as e:
        print(e)
        return make_response(jsonify({"error": "Unable to read course directory"}), 404)


@app.route('/<semester>/<course>/<lecture>')
def lecture_meta(semester, course, lecture):
    try:
        return json.dumps(media_parser.lecture_meta(semester, course, lecture))
    except OSError:
        return jsonify({"error": "Unable to read info file"}, 404)


@app.route('/<semester>/<course>/<lecture>/data')
def lecture_data(semester, course, lecture):
    try:
        return jsonify(media_parser.lecture_data(semester, course, lecture))
    except OSError:
        return jsonify({"error": "Unable to read lecture image directories"}), 404

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='set IMAGE_MEDIA_DIR in environment variable or provide a media directory')

    parser.add_argument('-m', '--media_dir', metavar='DIRECTORY', type=str, help='media directory')
    parser.add_argument('-d', '--debug', action='store_true', help='enable flask debugging')
    args = parser.parse_args()

    if args.media_dir:
        media_dir = args.media_dir
    elif 'IMAGE_MEDIA_DIR' in os.environ:
        media_dir = os.environ['IMAGE_MEDIA_DIR']
    else:
        parser.print_help()
        sys.exit()

    media_parser = media.ActualMedia(media_dir)

    app.run(host="0.0.0.0", port=int(os.environ.get("MEDIA_SERVER_PORT")) or 5000, debug=bool(args.debug))
