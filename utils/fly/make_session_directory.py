#!/usr/bin/env python3

import os
import logging


log = logging.getLogger(__name__)


def make_session_directory(context):
    """
    This function acquires the session.label and uses it to store the output
    of the algorithm.  This will keep the working output of the algorithm 
    separate from the bids input in work/bids.
    """

    try:
        # Create session_label in work directory
        session_dir = os.path.join(context.work_dir, 
                              context.gear_dict['session_label'])
        os.makedirs(session_dir,exist_ok=True)

    except Exception as e:
        context.gear_dict['session_label'] = 'error-unknown'
        log.error(e,)
        log.error('Unable to create session directory.')


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
