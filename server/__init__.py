import argparse
import os
from pathlib import Path

import flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import make_response, jsonify

from server.routes.index import cache as course_cache
from server.utils.constants import CONTAINER_MEDIA_DIR


def _register_blueprints(app):
    from server.routes.index import index
    app.register_blueprint(index)


def _register_error_handler(app):
    @app.errorhandler(KeyError)
    def handle_key_error(error: KeyError):
        return make_response(jsonify({"error": "key not found"}), 404)


def _parse_args():
    parser = argparse.ArgumentParser(
        usage='media micro service for parsing and caching course and their subsequent data'
    )
    parser.add_argument('-m', '--media_dir', metavar='DIRECTORY', type=str, help='media directory, provide a directory')
    parser.add_argument('-d', '--debug', action='store_true', help='enable flask debugging')

    return parser.parse_args()


def _parse_env_vars(args) -> dict:
    env_vars = {
        'port': os.environ.get('MEDIA_SERVER_PORT', 5000),
        'db_credentials': {
            'password': os.environ['MYSQL_ROOT_PASSWORD'],
            'db': os.environ['MYSQL_DATABASE'],
            'host': os.environ['MYSQL_HOSTNAME'],
            'user': os.environ['MYSQL_USER']
        }}
    env_vars.update(vars(args))

    return env_vars


def _configure_app():
    app = flask.Flask(__name__)

    return app


def _configure_task_runner():
    scheduler = BackgroundScheduler()

    from server.tasks.course_parsers import run
    scheduler.add_job(
        run,
        name='Course Parser',
        args=[course_cache],
        trigger=IntervalTrigger(minutes=15),
        id='parse_courses',
        replace_existing=True,
        coalesce=True
    )

    return scheduler


# TODO: This entire function is stupid, will be fixed later
def _insert_initial_data(db_credentials: dict):
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        return

    csv_path = os.path.join(CONTAINER_MEDIA_DIR, os.environ['USERS_CSV_PATH'])
    if csv_path and Path(csv_path).is_file():
        from server.tasks.insert_data import run
        run(csv_path, db_credentials)
        print("Inserted initial data")

    from server.tasks.insert_courses import run
    run(course_cache, db_credentials)
    print("Inserted initial courses")


def create_app():
    app = _configure_app()
    _register_blueprints(app)
    _register_error_handler(app)
    args = _parse_env_vars(_parse_args())
    task_runner = _configure_task_runner()
    _insert_initial_data(args['db_credentials'])

    return app, args, task_runner
