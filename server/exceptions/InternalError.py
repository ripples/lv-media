import sys
import traceback

from flask import jsonify


class InternalError(Exception):
    status_code = 500

    def __init__(self, error: Exception):
        Exception.__init__(self)
        self.message = str(error)

    @staticmethod
    def handle(error):
        response = jsonify({"error": "Something went wrong with the media server"})
        traceback.print_exception(*sys.exc_info())
        return response
