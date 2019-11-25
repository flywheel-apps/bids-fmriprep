# If you edit this file, please consider updating bids-app-template

import logging
import os
import shutil


log = logging.getLogger(__name__)


def find_freesurfer_license(context, fs_license_path):
    """ creates the Freesurfer license file at the given place in one of 3 ways """

    log.debug('')


    context.gear_dict['fs_license_found'] = False
    license_info = ''

    # Check if the required FreeSurfer license file has been provided
    # as an input file.
    fs_license_file = context.get_input_path('freesurfer_license')
    if fs_license_file:
        # TODO make sure this works, it has not been tested
        # just copy the file to the right place
        fs_path_only, fs_file = os.path.split(fs_license_path)
        if fs_file != 'license.txt':
            log.warning('Freesurfer license looks strange: ' + fs_license_path)
        if not os.path.exists(fs_path_only):
            os.makedirs(fs_path_only)
            log.warning('Had to make freesurfer license path: ' + fs_license_path)
        shutil.copy(fs_license_file, fs_license_path)
        context.gear_dict['fs_license_found'] = True
        log.info('Using FreeSurfer license in input file.')

    if not context.gear_dict['fs_license_found']:
        # see if it was passed as a string argument
        if context.config.get('gear-FREESURFER_LICENSE'):
            fs_arg = context.config['gear-FREESURFER_LICENSE']
            license_info = '\n'.join(fs_arg.split())
            context.gear_dict['fs_license_found'] = True
            log.info('Using FreeSurfer license in gear argument.')

    if not context.gear_dict['fs_license_found']:
        # TODO make sure this works, it has not been tested
        # see if it is in the project's info
        fw = context.client
        project_id = fw.get_analysis(context.destination.get('id')).parents.project
        project = fw.get_project(project_id)
        if project.info.get('FREESURFER_LICENSE'):
            license_info = '\n'.join(project.info.get('FREESURFER_LICENSE').split())
            context.gear_dict['fs_license_found'] = True
            log.info('Using FreeSurfer license in project info.')

    if not context.gear_dict['fs_license_found']:
        msg = 'Could not find FreeSurfer license in project info.'
        log.exception(msg)
        os.sys.exit(1)

    else:
        # if it was passed as a string or was found in info, save
        # the Freesuefer license as a file in the right place
        if license_info != '':

            head, tail = os.path.split(fs_license_path)

            if not os.path.exists(head):
                os.makedirs(head)

            with open(fs_license_path, 'w') as lf:
                lf.write(license_info)


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
