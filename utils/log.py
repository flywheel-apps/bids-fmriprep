# If you edit this file, please consider updating bids-app-template
"""
This is a user-modifiable file for Custom Logging
"""
import logging
import sys

def get_custom_logger(log_name):
    # Initialize Custom Logging
    # Timestamps with logging assist debugging algorithms
    # With long execution times
    handler = logging.StreamHandler(stream=sys.stdout)
    format = '%(levelname)s - %(name)-8s - %(asctime)s -  %(message)s'
    formatter = logging.Formatter(
                fmt=format,
                datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger = logging.getLogger(log_name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger

# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
