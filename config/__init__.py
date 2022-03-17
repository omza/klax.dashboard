"""
    initiate AppConfig

"""
import os
from sys import stderr, stdout, stdin

import logging
import logging.handlers

from config.configuration import AppConfiguration

config = AppConfiguration()

""" Logging Configuration """
logging.basicConfig(filename=config.LOG_FILE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=config.LOG_LEVEL)


