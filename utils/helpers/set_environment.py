#!/usr/bin/env python3
"""
"""

import logging

log = logging.getLogger(__name__)


def set_environment():

    # Let's ensure that we have our environment .json file and load it up
    exists(environ_json, log)

    # If it exists, read the file in as a python dict with json.load
    with open(environ_json, 'r') as f:
        log.info('Loading gear environment')
        environ = json.load(f)

    # Now set the current environment using the keys.  This will automatically be used with any sp.run() calls,
    # without the need to pass in env=...  Passing env= will unset all these variables, so don't use it if you do it
    # this way.
    for key in environ.keys():
        os.environ[key] = environ[key]

    # Pass back the environ dict in case the run.py program has need of it later on.
    return environ


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
