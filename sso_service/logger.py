import logging
import logging.handlers
import os

from sso_service.configuration import LOG_FILE_DIR


def config_logger(name, level, log_file_name=''):
    """Config a logging.Logger object and return it for use.

    Be careful not to call this function more than once with
    the same `name` value. Otherwise, multiple Handler
    instances with the same settings might be attached to the
    Logger instance with this name, thus producing duplicate
    log messages.

    :param name: name of the desired logger instance.
    :param level: log level.
    :param log_file_name: log file name.
    :return: A logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Don't propagate to root logger
    logger.propagate = False

    # Logger level
    level = getattr(logging, level.upper(), logging.NOTSET)
    logger.setLevel(level)

    # Path of log_file_name, will create the directory if not exists
    if not os.path.exists(LOG_FILE_DIR):
        os.makedirs(LOG_FILE_DIR)
    filename = os.path.join(LOG_FILE_DIR, log_file_name)

    # Handler (maxBytes, backupCount, encoding can be adjusted accordingly)
    fh = logging.handlers.RotatingFileHandler(filename,
                                              maxBytes=1024 * 1024 * 5,
                                              backupCount=100,
                                              encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Set Formatter of Handler
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(thread)d '
                                  '- %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Attach Handler to Logger
    logger.addHandler(fh)

    return logger
