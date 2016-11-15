from flask import jsonify


class NotFound(Exception):
    status_code = 404

    def __init__(self, message, payload=None):
        Exception.__init__(self)
        self._message = message
        self._payload = payload

    def to_dict(self):
        rv = dict(self._payload or ())
        rv["error"] = self._message
        return rv

    @staticmethod
    def handle_key_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
