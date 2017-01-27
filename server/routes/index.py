#! /usr/bin/env python3
from flask import abort, jsonify, Blueprint

from server.exceptions.NotFound import NotFound
from server.libs.parser import Parser

index = Blueprint('index', __name__)
parser = Parser()
cache = parser.read_all()


@index.route('/favicon.ico')
def root():
    abort(404)


@index.route('/semesters')
def semesters():
    return jsonify(list(cache.keys()))


@index.route('/<semester>')
def courses(semester):
    try:
        return jsonify(list(cache[semester].keys()))
    except KeyError as e:
        raise NotFound("{} not found".format(e))


@index.route('/<semester>/<course>')
def lectures(semester, course):
    try:
        return jsonify(cache[semester][course])
    except KeyError as e:
        raise NotFound("{} not found".format(e))


@index.route('/<semester>/<course>/<lecture>/data')
def lecture_data(semester, course, lecture):
    return jsonify(parser.lecture_data(semester, course, lecture))
