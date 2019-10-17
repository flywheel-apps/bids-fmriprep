# If you edit this file, please consider updating bids-app-template

import os, os.path as op
import subprocess as sp
import logging
import json
import pprint


log = logging.getLogger(__name__)


def download_bids(context):
    """ Download all files from the session in BIDS format
        bids_path will point to the local BIDS folder
        This creates a simiple dataset_description.json if
        one did not get downloaded.
    """

    log.debug('')

    bids_path = context.gear_dict['bids_path'] 

    # If BIDS was already downloaded, don't do it again
    # (this saves time when developing locally)
    if not op.isdir(bids_path):

        new_bids_path = context.download_session_bids(target_dir=bids_path)

        # Use the following command instead of he above (after core is 
	    # updated with a fix for it) because it will return the
	    # existing dataset_description.json file and does not download
	    # scans that don't need to be considered.  bids_path =
	    # context.download_project_bids(folders=['anat', 'func'])

        # Another way to get this file if there is an input is:
        #acq = fw.get_acquisition(context.get_input(<input key>)['hierarchy']['id'])
        #session = fw.get_session(acq.session)
        #project = fw.get_project(session.parents.project)
        #dataset_description = project.info.get(['BIDS'])

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
