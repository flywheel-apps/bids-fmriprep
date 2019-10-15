#!/usr/bin/env python3
"""
"""

import logging


log = logging.getLogger(__name__)


def import_dicom_header_as_dict(dcm_filepath, tag_keyword_list):
    """
    Generates a dictionary of DICOM tag-DICOM tag value key-value pairs given a filepath to a valid DICOM file
    :param dcm_filepath: path to an individual DICOM image
    :type dcm_filepath: str
    :param tag_keyword_list: a list of DICOM tags to acquire
    :type tag_keyword_list: list
    :param log: a Logger instance
    :type log: logging.Logger
    :return: a dictionary with DICOM tag-DICOM tag value key-value pairs, returns empty dict if not a valid DICOM file
    :rtype: dict
    """
    header_dict = dict()
    try:
        dataset = pydicom.read_file(dcm_filepath)
    except pydicom.filereader.InvalidDicomError:
        log.warning('Invalid DICOM file: {}'.format(dcm_filepath))
        return header_dict

    for element in dataset:
        if element.keyword in tag_keyword_list:
            key = element.keyword
            value = element.value
            header_dict[key] = str(value)
    return header_dict


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
