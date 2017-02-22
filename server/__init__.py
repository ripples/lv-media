import argparse
import os
from datetime import datetime, timedelta

import flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from server.libs.database import connect
from server.routes.index import courses_cache
from server.utils.constants import CONTAINER_MEDIA_DIR

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _register_blueprints(app):
    from server.routes.index import index
    app.register_blueprint(index)


def _register_error_handlers(app):
    from server.exceptions.NotFound import NotFound
    app.register_error_handler(NotFound, NotFound.handle_key_error)


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
        'lv-server-host': os.environ.get('SERVER_HOSTNAME', 'lv-server'),
        'lv-server-port': os.environ.get('SERVER_PORT', 3000),
        'environment': os.environ.get('NODE_ENV', 'development'),
        'WERKZEUG_RUN_MAIN': os.environ.get('WERKZEUG_RUN_MAIN', 'false'),
        'dev_email': os.environ.get('DEV_EMAIL', None),
    }
    env_vars.update(vars(args))

    return env_vars


def _configure_app():
    app = flask.Flask(__name__)

    return app


def _configure_task_runner(app_args):
    # We don't want to reload the task runner when flask reloads
    if app_args['WERKZEUG_RUN_MAIN'] != 'true':
        return

    scheduler = BackgroundScheduler()

    from server.tasks.cache_fs_courses import run
    scheduler.add_job(
        run,
        name='Cache Courses From File System',
        args=[courses_cache],
        trigger=IntervalTrigger(minutes=15),
        id='cache_fs_courses',
        replace_existing=True,
        coalesce=True
        # next run time = loaded immediately in index route
    )

    from server.tasks.insert_fs_courses import run
    scheduler.add_job(
        run,
        name='Insert Courses From File System',
        args=[courses_cache],
        trigger=IntervalTrigger(days=1),
        id='insert_fs_courses',
        replace_existing=False,
        coalesce=True,
        next_run_time=datetime.today() + timedelta(minutes=5)
    )

    from server.tasks.insert_users_and_courses import run
    scheduler.add_job(
        run,
        name='Insert Users and Courses',
        trigger=IntervalTrigger(minutes=30),
        id='insert_users_and_courses',
        replace_existing=False,
        coalesce=True,
        next_run_time=datetime.today() + timedelta(minutes=10)
    )

    from server.tasks.invite_users import run
    scheduler.add_job(
        run,
        name='Invite Users',
        args=[app_args],
        trigger=IntervalTrigger(days=1),
        id='invite_users',
        replace_existing=False,
        coalesce=True,
        next_run_time=datetime.today() + timedelta(minutes=15)
    )

    return scheduler


def _setup_dev(dev_email: str):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute("""
        UPDATE users
        SET password = '$2a$10$JofcKIcaYmEaFudtzfuAfuFpwLPe3t/czs/cKdsz0IEdieXmWnu76'
        WHERE email = %s""", dev_email)
        logger.debug("Inserted dev user {}", dev_email)


def create_app():
    app = _configure_app()
    _register_blueprints(app)
    _register_error_handlers(app)
    args = _parse_env_vars(_parse_args())
    task_runner = _configure_task_runner(args)
    if args["environment"] == "development":
        _setup_dev(args["dev_email"])

    return app, args, task_runner
