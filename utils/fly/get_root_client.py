#!/usr/bin/env python3

import logging
import re


log = logging.getLogger(__name__)


def get_root_client(fw_client):
    """
    Takes a flywheel client and gives it root mode if the user is site admin, otherwise just returns the input client
    :param fw_client: an instance of the flywheel client
    :type fw_client: flywheel.client.Client
    :param log: a Logger instance
    :type log: logging.Logger
    :return: fw_client: an instance of the flywheel client with root mode enabled if user is site admin
    """

    # parse the "url:" part of the api key from the site url
    site_url = fw_client.get_config().site.api_url
    site_patt = re.compile('https:\/\/(.*:).*')
    site_url = site_patt.match(site_url).group(1)
    user = fw_client.get_current_user()
    api_key = user.api_key.key
    # If the user is not admin, warn and return the input client
    if 'site_admin' in user.get('roles'):
        log.warning('User {} is not a site admin. Root mode will not be enabled.'.format(user.id))
        log.warning('User roles: {}'.format(user['roles']))
    else:
        fw_client = flywheel.Client(site_url+api_key, root=True)
    return fw_client


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
