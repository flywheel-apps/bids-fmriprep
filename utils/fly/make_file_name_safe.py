# If you edit this file, please consider updating bids-app-template

import logging
import re


log = logging.getLogger(__name__)


def make_file_name_safe(input_basename, replace_str=''):
    """
    removes non-safe characters from a filename and returns a filename with these characters replaced with replace_str
    :param input_basename: the input basename of the file to be replaced
    :type input_basename: str
    :param log: a logger instance
    :type log: logging.Logger
    :param replace_str: the string with which to replace the unsafe characters
    :type   replace_str: str
    :return: output_basename, a safe
    :rtype: str
    """
    import re

    log.debug('')

    safe_patt = re.compile('[^A-Za-z0-9_\.]+')
    # if the replacement is not a string or not safe, set replace_str to x
    if not isinstance(replace_str, str) or safe_patt.match(replace_str):
        log.warning('{} is not a safe string, removing instead'.format(replace_str))
        replace_str = ''

    # Replace non-alphanumeric (or underscore) characters with replace_str
    safe_output_basename = re.sub(safe_patt, replace_str, input_basename)

    log.debug('"' + input_basename + '" -> "' + safe_output_basename + '"')

    return safe_output_basename


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
