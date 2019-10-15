#!/usr/bin/env python3
"""
"""

import logging


log = logging.getLogger(__name__)


def exists(file, is_expected=True, quit_on_error=True):
    # Generic if_exists function that takes care of logging in the event of nonexistance
    # is_expected indicates if we're checking to see if it's there or not. True: we want it to be there, false: we don't
    # quit_on_error tells us if we sys.exit on failure or not.

    path_exists=os.path.exists(file)

    # If we find the file and are expecting to
    if path_exists and is_expected:
        log.info('located {}'.format(file))

    # If we don't find the file and are expecting to
    elif not path_exists and is_expected:
        # and if that file is critical
        if quit_on_error:
            # Quit the program
            log.error('Unable to locate {} '.format(file))
            sys.exit(1)
            # Otherwise, we'll manage.  Keep on trucking.
        else:
            log.warning('Unable to locate {} '.format(file))

    # If we don't find the file and we weren't expecting to:
    elif not path_exists and not is_expected:
        # Then we're all good, keep on trucking
        log.info('{} is not present or has been removed successfully'.format(file))

    # If we don't expect the file to be there, but it is...DUN DUN DUNNNN
    elif path_exists and not is_expected:
        # and if that file is critical
        if quit_on_error:
            # Well, you know the drill by now.
            log.error('file {} is present when it must be removed'.format(file))
            sys.exit(1)
        else:
            log.warning('file {} is present when it should be removed'.format(file))

    return path_exists


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
