#!/usr/bin/env python3
"""
Things that go zip or unzip
"""
import logging


log = logging.getLogger(__name__)


def extract_return_paths(input_filepath):
    """
    Extracts a zip archive to a temporary directory and
    returns a list of paths of the files.  Does not delete
    the temporary directory.
    :param input_filepath:  a path to a zip archive
    :type input_filepath: str
    :return: file_list, a list of paths to the extracted files
    :rtype: list of str
    """
    if zipfile.is_zipfile(input_filepath):
        # Make a temporary directory
        temp_dirpath = tempfile.mkdtemp()
        # Extract to this temporary directory
        with zipfile.ZipFile(input_filepath) as zip_object:
            zip_object.extractall(temp_dirpath)
            # Return the list of paths
            file_list = zip_object.namelist()
            # Get full paths and remove directories from list
            file_list = [os.path.join(temp_dirpath, file) for file in file_list if not file.endswith('/')]
    else:
        log.warning('Not a zip. Attempting to read {} directly'.format(os.path.basename(input_filepath)))
        file_list = [input_filepath]
    return file_list


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
