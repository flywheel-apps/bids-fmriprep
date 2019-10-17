#!/usr/bin/env python3
"""
Functions that get info from Flywheel client, mmmmm helpful!
"""

import logging
import json


log = logging.getLogger(__name__)


def load_manifest_json():
    """
    load the /flywheel/v0/manifest.json file as a dictionary
    :return: manifest_json
    :rtype: dict
    """

    log.debug('')

    config_file_path = '/flywheel/v0/manifest.json'
    with open(config_file_path) as manifest_data:
        manifest_json = json.load(manifest_data)
    return manifest_json


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
