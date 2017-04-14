#! /usr/bin/env python3
from flask import abort, jsonify, Blueprint

from server.exceptions.InternalError import InternalError
from server.exceptions.NotFound import NotFound
from server.libs.parser import Parser

index = Blueprint('index', __name__)
parser = Parser()
courses_cache = parser.read_all()


@index.route('/favicon.ico')
def root():
    abort(404)


@index.route('/semesters')
def semesters():
    try:
        return jsonify(list(courses_cache.keys()))
    except Exception as e:
        raise InternalError(e)


@index.route('/<semester>')
def courses(semester):
    try:
        return jsonify(list(courses_cache[semester].keys()))
    except KeyError as e:
        raise NotFound("{} not found".format(e))
    except Exception as e:
        raise InternalError(e)


@index.route('/<semester>/<course>')
def lectures(semester, course):
    try:
        return jsonify(courses_cache[semester][course])
    except KeyError as e:
        raise NotFound("{} not found".format(e))
    except Exception as e:
        raise InternalError(e)


@index.route('/<semester>/<course>/<lecture>/data')
def lecture_data(semester, course, lecture):
    try:
        return jsonify(parser.lecture_data(semester, course, lecture))
    except Exception as e:
        raise InternalError(e)
