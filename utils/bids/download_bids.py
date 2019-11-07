# If you edit this file, please consider updating bids-app-template

import os, os.path as op
import subprocess as sp
import logging
import json
import pprint


log = logging.getLogger(__name__)


def download_bids(context, src_data=False, subjects=None, sessions=None, folders=None, **kwargs):
    """ Download all files from the session in BIDS format
        bids_path will point to the local BIDS folder
        This creates a simple dataset_description.json if
        one did not get downloaded.
    """

    bids_path = context.gear_dict['bids_path'] 

    log.info('Downloading into: ' + bids_path)

    # If BIDS was already downloaded, don't do it again
    # (this saves time when developing locally)
    if not op.isdir(bids_path):

        # bool src_data: Whether or not to include src data (e.g. dicoms)
        # list subjects: The list of subjects to include (via subject code) otherwise all subjects
        # list sessions: The list of sessions to include (via session label) otherwise all sessions
        # list folders: The list of folders to include (otherwise all folders) e.g. ['anat', 'func']
        # **kwargs: Additional arguments to pass to download_bids_dir
        new_bids_path = context.download_project_bids('work/bids', src_data, subjects, sessions, folders)

        # def download_project_bids(self, target_dir='work/bids', src_data=False, subjects=None, sessions=None,
        #                          folders=None, **kwargs):

        # Another way to get this file if there is an input is:
        # acq = fw.get_acquisition(context.get_input(<input key>)['hierarchy']['id'])
        # session = fw.get_session(acq.session)
        # project = fw.get_project(session.parents.project)
        # dataset_description = project.info.get(['BIDS'])

        if new_bids_path != bids_path:
            # bids_path in run.py needs to match what is returned by
            # context.download_session_bids() so change it to this new
            # place.
            raise Exception('Unexpected BIDS path "' + new_bids_path + '"')
            os.sys.exit(-1)

        # make sure dataset_description.json exists
        # Is there a way to download the dataset_description.json file from the 
        # platform instead of creating a generic stub?
        required_file = bids_path + '/dataset_description.json'
        if not op.exists(required_file):
            log.info('Creating missing '+required_file+'.')
            the_stuff = {
                "Acknowledgements": "",
                "Authors": [],
                "BIDSVersion": "1.2.0",
                "DatasetDOI": "",
                "Funding": "",
                "HowToAcknowledge": "",
                "License": "",
                "Name": "tome",
                "ReferencesAndLinks": [],
                "template": "project"
            }
            with open(required_file, 'w') as outfile:
                json.dump(the_stuff, outfile)
        else:
            log.info(required_file+' exists.')

        log.info('BIDS was downloaded into '+bids_path)

    else:
        log.info('Using existing BIDS path '+bids_path)
    
    context.gear_dict['bids_path'] = bids_path


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
