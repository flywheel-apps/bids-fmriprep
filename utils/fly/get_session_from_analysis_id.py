#!/usr/bin/env python3

import os
import logging


log = logging.getLogger(__name__)


def get_session_from_analysis_id(fw_client, input_analysis_id):
    """
    Returns the session associated with the input analysis id (if the parent is a session)
    :param fw_client: an instance of the flywheel client
    :type fw_client: flywheel.client.Client
    :param input_analysis_id: the id for the analysis container
    :type input_analysis_id: str
    :return: session, a flywheel session associated with the analysis
    :rtype: flywheel.models.session.Session
    """
    try:
        # Grab time for logging how long session get takes
        func_time_start = time.time()
        analysis = fw_client.get_analysis(input_analysis_id)
        session = fw_client.get_session(analysis.parent.id)

        log.info('Session ID is: {}'.format(session.get('_id')))
        if type(session) != flywheel.models.session.Session \
                or not session:
            log.error('{} is not a session. This gear must be run from the session level.'.format(analysis.parent.id))
            os.sys.exit(1)

        else:
            func_time_end = time.time()
            log.debug('It took {} seconds to get session'.format(func_time_end - func_time_start))
            return session

    except flywheel.ApiException as e:
        log.error('Exception encountered when getting session from analysis {}: {}'.format(input_analysis_id, e))
        os.sys.exit(1)


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
