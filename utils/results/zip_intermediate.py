# If you edit this file, please consider updating bids-app-template

import os
import logging
import subprocess as sp


log = logging.getLogger(__name__)


def zip_intermediate_selected(context):
    """
    Find all of the listed files and folders in the "work/" directory and zip 
    them into one archive.
    """

    log.debug('')

    # Name of zip file has <subject> and <analysis>
    subject = context.gear_dict['subject_code']
    analysis_id = context.destination['id']
    file_name = 'fmriprep_work_selected_' + subject + '_' + analysis_id + '.zip'
    dest_zip = os.path.join(context.output_dir,file_name)

    do_find = False
    # get list of intermediate files (if any)
    if isinstance(context.config['gear-intermediate-files'],str):
        if len(context.config['gear-intermediate-files']) > 0:
            files = context.config['gear-intermediate-files'].split()
            do_find = True

    # get list of intermediate folders (if any)
    if isinstance(context.config['gear-intermediate-folders'],str):
        if len(context.config['gear-intermediate-folders']) > 0:
            folders = context.config['gear-intermediate-folders'].split()
            do_find = True

    os.chdir(context.work_dir)

    if do_find:
        log.info('Files and folders will be zipped to "' + dest_zip + '"')
        for subdir, walk_dirs, walk_files in os.walk('.'):
            for ff in walk_files:
                if ff in files:
                    path = os.path.join(subdir, ff)
                    log.info('Zipping file:   ' + path)
                    command = ['zip', '-q', dest_zip, path]
                    result = sp.run(command, check=True)
            for ff in walk_dirs:
                if ff in folders:
                    print('subdir = ' + subdir)
                    print('ff     = ' + ff)
                    path = os.path.join(subdir, ff)
                    log.info('Zipping folder: ' + path)
                    command = ['zip', '-q', '-r', dest_zip, path]
                    result = sp.run(command, check=True)


def zip_all_intermediate_output(context):
    """
    Zip all intermediate output in the "work/ directory into one archive.
    """

    log.debug('')

    # Name of zip file has <subject> and <analysis>
    subject = context.gear_dict['subject_code']
    analysis_id = context.destination['id']
    file_name = 'fmriprep_work_' + subject + '_' + analysis_id + '.zip'
    dest_zip = os.path.join(context.output_dir,file_name)

    work_path, work_dir = os.path.split(context.work_dir)
    os.chdir(work_path)

    log.info(
        'Zipping ' + work_dir + ' directory to ' + dest_zip + '.'
    )

    command = ['zip', '-q', '-r', dest_zip, work_dir]
    result = sp.run(command, check=True)


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
