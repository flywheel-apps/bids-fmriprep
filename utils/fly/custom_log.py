# If you edit this file, please consider updating bids-app-template
"""
This is a user-modifiable file for Custom Logging
"""

import logging
import sys


def custom_log(gear_context):
    """
    Generate a log with level and name configured for the suite, gear name and gear-log-level
    :param gear_context: an instance of the flywheel gear context that includes the manifest_json attribute
    :type gear_context: flywheel.gear_context.GearContext
    :return: log
    :rtype: logging.Logger
    """

    log_level = gear_context.config.get('gear-log-level', 'INFO')

    # Set suite (default to flywheel)
    try:
        suite = gear_context.manifest_json['custom']['flywheel']['suite']
    except KeyError:
        suite = 'flywheel'

    # Set gear_name
    gear_name = gear_context.manifest_json['name']

    log_name = '/'.join([suite, gear_name])

    # Tweak the formatting
    fmt = '%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s %(funcName)s()]: %(message)s'
    logging.basicConfig(level=log_level, format=fmt, 
                        datefmt='%Y-%m-%d %H:%M:%S')
    log = logging.getLogger(log_name)
    log.critical('{} log level is {}'.format(log_name, log_level))
    return log


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
