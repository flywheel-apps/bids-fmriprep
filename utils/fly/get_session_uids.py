#!/usr/bin/env python3

import os
import logging
import json


log = logging.getLogger(__name__)


def get_session_uids(session, output_path):
    """
    Writes all unique UIDs for the input session to the output_path and returns the corresponding dictionary
    :param session: a flywheel session
    :type session: flywheel.models.session.Session
    :param output_path: the directory to which to write the json file containing session Study/SeriesInstanceUIDs
    :type output_path: str
    :param log: a Logger instance
    :type log: logging.Logger
    :return: session_dict, a dictionary containing session StudyInstanceUIDs and SeriesInstanceUIDs
    :rtype: dict
    """
    tag_list = ['SeriesInstanceUID', 'StudyInstanceUID']
    log.info('Getting UID info for session {} ({})'.format(session.id, session.label))
    session_dict = dict()

    for acquisition in session.acquisitions():
        log.info('Getting UID info for acquisition {} ({})'.format(acquisition.id, acquisition.label))
        acquisition = acquisition.reload()
        dicom_count = 0
        UID_entry_count = 0
        for file in acquisition.files:
            if file.type == 'dicom':
                log.debug('Processing DICOM: {}'.format(file.name))
                dicom_count += 1
                download_directory = tempfile.mkdtemp()
                try:
                    # Get a single image from the DICOM archive if possible
                    zip_member_file = file.get_zip_info().members[0]['path']
                    safe_file_name = make_file_name_safe(zip_member_file, log)
                    download_path = os.path.join(download_directory, safe_file_name)
                    file.download_zip_member(zip_member_file, download_path)
                    dicom_file_list = [download_path]
                # if can't get zip file member, download the whole archive
                except Exception as e:
                    log.warning('Could not access zip members:')
                    log.warning(e)
                    log.info('Downloading entire DICOM archive')
                    # Replace non-alphanumeric (or underscore) characters with x
                    safe_zip_name = make_file_name_safe(file.name, log)
                    download_path = os.path.join(download_directory, safe_zip_name)
                    file.download(download_path)
                    if zipfile.is_zipfile(download_path):
                        dicom_file_list = extract_return_path(download_path)
                    else:
                        dicom_file_list = [download_path]
                # import the dicom header info
                log.debug('Reading {}'.format(download_path))
                dicom_dict = import_dicom_header_as_dict(dicom_file_list[-1], tag_list, log)

                # Confirm that UIDs exist
                if not dicom_dict.get('StudyInstanceUID'):
                    log.error('No StudyInstanceUID present for file: {}'.format(file.name))
                if not dicom_dict.get('SeriesInstanceUID'):
                    log.error('No SeriesInstanceUID present for file: {}'.format(file.name))
                # Create key if it doesn't exist
                if dicom_dict.get('StudyInstanceUID'):
                    UID_entry_count += 1
                    if not session_dict.get(dicom_dict.get('StudyInstanceUID')):
                        session_dict[dicom_dict['StudyInstanceUID']] = list()
                    session_dict[dicom_dict['StudyInstanceUID']].append(dicom_dict['SeriesInstanceUID'])
                # Remove the extracted DICOM images
                shutil.rmtree(os.path.dirname(dicom_file_list[0]))
                # Remove the download zip
                if os.path.isdir(download_directory):
                    shutil.rmtree(download_directory)
                if session_dict:
                    with open(output_path, 'w') as f:
                        json.dump(session_dict, f, separators=(', ', ': '), indent=4)
        if dicom_count != UID_entry_count:
            log.error('expected {} StudyInstanceUIDs, found {}'.format(dicom_count, UID_entry_count))
            os.sys.exit(1)

    return session_dict


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
