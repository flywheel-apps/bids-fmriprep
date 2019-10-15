#!/usr/bin/env python3

import logging
import re


log = logging.getLogger(__name__)


def set_session_label(context):
    """

    # This is used by args.make_session_directory() and 
    #                 results.zip_output()

    """
    # TODO will this work for a non-admin user?

    try:
        fw = context.client

        dest_container = fw.get(context.destination['id'])

        session_id = dest_container.get('session')

        if session_id is None:
            session_id = dest_container.get('parents', {}).get('session')

        # Kaleb says 
        # TODO   Better to get the session information from
        #        context.get_input()['hierarchy']['id'] for a specific input.
        #        This also allows the template to accommodate inputs from different
        #        sessions.

        if session_id is None:
            log.error('Cannot get session label from destination')
            context.gear_dict['session_label'] = 'session_unknown'

        else:
            session = fw.get(session_id)
            session_label = re.sub('[^0-9a-zA-Z./]+', '_', session.label)
            # attach session_label to gear_dict
            context.gear_dict['session_label'] = session_label

        log.debug('Session label is "' + session_label + '"')

    except Exception as e:
        # report error and go on in case there are more errors to report
        context.gear_dict['errors'].append(e)
        log.critical(e,)
        log.exception('Error in set_session_label()',)


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
