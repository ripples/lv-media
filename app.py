#!/usr/bin/env python
import logging
from logging.handlers import TimedRotatingFileHandler
from server import create_app

app, _args, _task_runner = create_app()


def _configure_logging():
    # System wide logging
    logger = logging.getLogger()

    log_fh = TimedRotatingFileHandler('logs/log', when='midnight', backupCount=30)
    log_fh.suffix = '%Y_%m_%d'
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)"')
    log_fh.setFormatter(formatter)

    stderr_fh = logging.StreamHandler()

    logger.addHandler(log_fh)
    logger.addHandler(stderr_fh)
    logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    _configure_logging()
    logging.info('Starting task runner')
    _task_runner.start()
    logging.info('Starting server')
    app.run(host="0.0.0.0", port=int(_args['port']) or 5000, debug=bool(_args['debug']))
