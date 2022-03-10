"""
    initiate AppConfig

"""
import os
from sys import stderr, stdout, stdin

import logging
import logging.handlers

from .configuration import AppConfiguration

config = AppConfiguration()

""" Logging Configuration """
log = logging.getLogger(config.MAINLOGGER)

formatter = logging.Formatter('%(asctime)s | %(name)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s')

consolehandler = logging.StreamHandler(stdout)
consolehandler.setFormatter(formatter)
consolehandler.setLevel(config.LOGLEVEL_CONSOLE)
    
logfilename = config.FULL_PATH_LOG
filehandler = logging.handlers.RotatingFileHandler(logfilename, 10240, 5)
filehandler.setFormatter(formatter)
filehandler.setLevel(config.LOGLEVEL_FILE)

log.setLevel(config.LOGLEVEL_CONSOLE)
log.addHandler(consolehandler)
log.addHandler(filehandler)

