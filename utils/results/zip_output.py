# If you edit this file, please consider updating bids-app-template

import os
import logging
import subprocess as sp


log = logging.getLogger(__name__)


def zip_output(context):
    """Create zipped results"""


    # This executes regardless of errors or exit status,

    # Zip file name has <subject> and <analysis>
    subject = context.gear_dict['subject']
    analysis_id = context.destination['id']
    file_name = 'fmriprep_' + subject + '_' + analysis_id + '.zip'
    dest_zip = os.path.join(context.output_dir,file_name)

    # fmriprep output went into output/analysis_id/...
    os.chdir(context.output_dir)
    actual_dir = context.destination['id']

    log.info(
        'Zipping ' + actual_dir + ' directory to ' + dest_zip + '.'
    )
    command = ['zip', '-q', '-r', dest_zip, actual_dir]
    result = sp.run(command, check=True)


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
