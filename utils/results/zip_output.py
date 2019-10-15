# If you edit this file, please consider updating bids-app-template

import os
import logging
import subprocess as sp


log = logging.getLogger(__name__)


def zip_output(context):
    # Cleanup, create manifest, create zipped results,
    # move all results to the output directory
    # This executes regardless of errors or exit status,
    os.chdir(context.work_dir)
    # If the output/result.anat path exists, zip regardless of exit status
    # Clean input_file_basename to lack esc chars and extension info

    # Grab Session label
    session_label = context.gear_dict['session_label']
    dest_zip = os.path.join(context.output_dir,session_label + '.zip')

    if os.path.exists(os.path.join(context.work_dir,session_label)):
        log.info(
            'Zipping ' + session_label + ' directory to ' + dest_zip + '.'
        )
        # For results with a large number of files, provide a manifest.
        # Capture the stdout/stderr in a file handle or for logging.
        manifest = os.path.join(
            context.output_dir, session_label + '_output_manifest.txt'
        )
        command0 = ['tree', '-shD', '-D', session_label]
        with open(manifest, 'w') as f:
            result0 = sp.run(command0, stdout = f)
        command1 = ['zip', '-r', dest_zip, session_label]
        result1 = sp.run(command1, stdout=sp.PIPE, stderr=sp.PIPE)
    else:
        log.info(
            'No results directory, ' + \
            os.path.join(context.work_dir,session_label) + \
            ', to zip.'
        )


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
