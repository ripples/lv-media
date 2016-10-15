import argparse
import flask
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


def _register_blueprints(app):
    from server.routes.index import index
    app.register_blueprint(index)


def _parse_args():
    parser = argparse.ArgumentParser(
        usage='media micro service for parsing and caching course and their subsequent data'
    )
    parser.add_argument('-m', '--media_dir', metavar='DIRECTORY', type=str,
                        help='media directory, set IMAGE_MEDIA_DIR in environment variable or provide a directory')
    parser.add_argument('-d', '--debug', action='store_true', help='enable flask debugging')

    return parser.parse_args()


def _parse_env_vars(args) -> dict:
    env_vars = {}
    if not hasattr(args, 'media_dir'):
        if 'IMAGE_MEDIA_DIR' in os.environ:
            env_vars['media_dir'] = os.environ['IMAGE_MEDIA_DIR']
        else:
            raise Exception('set IMAGE_MEDIA_DIR in environment variable or provide a directory')

    env_vars['port'] = os.environ.get('MEDIA_SERVER_PORT') or 5000
    env_vars.update(vars(args))

    return env_vars


def _configure_app():
    app = flask.Flask(__name__)

    return app


def _configure_task_runner():
    scheduler = BackgroundScheduler()

    from server.tasks.parse_courses import run
    from server.routes.index import cache
    scheduler.add_job(
        run,
        args=[cache],
        trigger=IntervalTrigger(minutes=15),
        id='parse_courses',
        replace_existing=True,
        coalesce=True
    )

    return scheduler


def create_app():
    app = _configure_app()
    _register_blueprints(app)
    args = _parse_env_vars(_parse_args())
    task_runner = _configure_task_runner()

    return app, args, task_runner
