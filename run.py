#!/usr/bin/env python3
""" Run the gear: set up for and call command-line code """

import json
import os
import subprocess as sp
import sys
import shutil
import psutil
import glob

import flywheel
from utils import args
from utils.bids.download_bids import *
from utils.bids.validate_bids import *
from utils.fly.custom_log import *
from utils.fly.load_manifest_json import *
from utils.fly.make_file_name_safe import *
from utils.results.set_zip_name import set_zip_head
from utils.results.zip_htmls import zip_htmls
from utils.results.zip_output import zip_output
from utils.results.zip_intermediate import zip_all_intermediate_output
from utils.results.zip_intermediate import zip_intermediate_selected
from utils.results.zip_intermediate import zip_intermediate_selected
import utils.dry_run


def initialize(context):

    # Add manifest.json as the manifest_json attribute
    setattr(context, 'manifest_json', load_manifest_json())

    log = custom_log(context)

    context.log_config() # not configuring the log but logging the config

    # Instantiate custom gear dictionary to hold "gear global" info
    context.gear_dict = {}

    # The main command line command to be run:
    context.gear_dict['COMMAND'] = 'fmriprep'

    # Keep a list of errors and warning to print all in one place at end of log
    # Any errors will prevent the command from running and will cause exit(1)
    context.gear_dict['errors'] = []  
    context.gear_dict['warnings'] = []

    # Get level of run from destination's parent: subject or session
    fw = context.client
    dest_container = fw.get(context.destination['id'])
    context.gear_dict['run_level'] = dest_container.parent.type
    log.info('Running at the ' + context.gear_dict['run_level'] + ' level.')

    project_id = dest_container.parents.project
    context.gear_dict['project_id'] = project_id
    if project_id:
        project = fw.get(project_id)
        context.gear_dict['project_label'] = project.label
        context.gear_dict['project_label_safe'] = \
            make_file_name_safe(project.label, '_')
    else:
        context.gear_dict['project_label'] = 'unknown_project'
        context.gear_dict['project_label_safe'] = 'unknown_project'
        log.warning('Project label is ' + context.gear_dict['project_label'])

    subject_id = dest_container.parents.subject
    context.gear_dict['subject_id'] = subject_id
    if subject_id:
        subject = fw.get(subject_id)
        context.gear_dict['subject_code'] = subject.code
        context.gear_dict['subject_code_safe'] = \
            make_file_name_safe(subject.code, '_')
    else:
        context.gear_dict['subject_code'] = 'unknown_subject'
        context.gear_dict['subject_code_safe'] = 'unknown_subject'
        log.warning('Subject code is ' + context.gear_dict['subject_code'])

    session_id = dest_container.parents.session
    context.gear_dict['session_id'] = session_id
    if session_id:
        session = fw.get(session_id)
        context.gear_dict['session_label'] = session.label
        context.gear_dict['session_label_safe'] = \
            make_file_name_safe(session.label, '_')
    else:
        context.gear_dict['session_label'] = 'unknown_session'
        context.gear_dict['session_label_safe'] = 'unknown_session'
        log.warning('Session label is ' + context.gear_dict['session_label'])

    # Set first part of result zip file names based on the above file safe names
    set_zip_head(context)

    # the usual BIDS path:
    bids_path = os.path.join(context.work_dir, 'bids')
    context.gear_dict['bids_path'] = bids_path

    # in the output/ directory, add extra analysis_id directory name for easy
    #  zipping of final outputs to return.
    context.gear_dict['output_analysisid_dir'] = \
        context.output_dir + '/' + context.destination['id']

    # get # cpu's to set --n_cpus argument
    cpu_count = os.cpu_count()
    log.info('os.cpu_count() = ' + str(cpu_count))
    context.gear_dict['cpu_count'] = cpu_count

    log.info('psutil.virtual_memory().total= {:4.1f} GiB'.format(
                      psutil.virtual_memory().total / (1024 ** 3)))
    log.info('psutil.virtual_memory().available= {:4.1f} GiB'.format(
                      psutil.virtual_memory().available / (1024 ** 3)))

    # grab environment for gear
    with open('/tmp/gear_environ.json', 'r') as f:
        environ = json.load(f)
        context.gear_dict['environ'] = environ

        # Add environment to log if debugging
        kv = ''
        for k, v in environ.items():
            kv += k + '=' + v + ' '
        log.debug('Environment: ' + kv)

    return log


def create_command(context, log):

    # Create the command and validate the given arguments
    try:

        # Set the actual gear command:
        command = [context.gear_dict['COMMAND']]

        # 3 positional args: bids path, output dir, 'participant'
        # This should be done here in case there are nargs='*' arguments
        # These follow the BIDS Apps definition (https://github.com/BIDS-Apps)
        command.append(context.gear_dict['bids_path'])
        command.append(context.gear_dict['output_analysisid_dir'])
        command.append('participant')

        # Put command into gear_dict so arguments can be added in args.
        context.gear_dict['command'] = command

        # Process inputs, contextual values and build a dictionary of
        # key-value arguments specific for COMMAND
        args.get_inputs_and_args(context)

        # Validate the command parameter dictionary - make sure everything is 
        # ready to run so errors will appear before launching the actual gear 
        # code.  Raises Exception on fail
        args.validate(context)

        # Build final command-line (a list of strings)
        command = args.build_command(context)

    except Exception as e:
        context.gear_dict['errors'].append(e)
        log.critical(e)
        log.exception('Error in creating and validating command.',)


def set_up_data(context, log):
    # Set up and validate data to be used by command
    try:

        # Download bids for the current session 
        # bool src_data: Whether or not to include src data (e.g. dicoms) default: False
        # list subjects: The list of subjects to include (via subject code) otherwise all subjects
        # list sessions: The list of sessions to include (via session label) otherwise all sessions
        # list folders: The list of folders to include (otherwise all folders) e.g. ['anat', 'func']
        # **kwargs: Additional arguments to pass to download_bids_dir

        folders_to_load = ['anat', 'func', 'fmap']

        if context.gear_dict['run_level'] == 'project':

            log.info('Downloading BIDS for project "' + 
                     context.gear_dict['project_label'] + '"')

            # don't filter by subject or session, grab all
            download_bids(context, folders=folders_to_load)

        elif context.gear_dict['run_level'] == 'subject':

            log.info('Downloading BIDS for subject "' + 
                     context.gear_dict['subject_code'] + '"')

            # filter by subject
            download_bids(context, 
                      subjects = [context.gear_dict['subject_code']],
                      folders=folders_to_load)

        elif context.gear_dict['run_level'] == 'session':

            log.info('Downloading BIDS for session "' + 
                     context.gear_dict['session_label'] + '"')

            # filter by session
            download_bids(context, 
                      subjects = [context.gear_dict['subject_code']],
                      sessions = [context.gear_dict['session_label']],
                      folders=folders_to_load)

        else:
            msg = 'This job is not being run at the project subject or ' +\
                  'session level'
            raise TypeError(msg)

        # Validate Bids file heirarchy
        # Bids validation on a phantom tree may be occuring soon
        validate_bids(context)

    except Exception as e:
        context.gear_dict['errors'].append(e)
        log.critical(e)
        log.exception('Error in BIDS download and validation.',)


def execute(context, log):
    try:

        log.info('Command: ' + ' '.join(context.gear_dict['command']))

        # Don't run if there were errors or if this is a dry run
        ok_to_run = True

        if len(context.gear_dict['errors']) > 0:
            ok_to_run = False
            result = sp.CompletedProcess
            result.returncode = 1
            log.info('Command was NOT run because of previous errors.')

        elif context.config['gear-dry-run']:
            ok_to_run = False
            result = sp.CompletedProcess
            result.returncode = 0
            e = 'gear-dry-run is set: Command was NOT run.'
            log.warning(e)
            context.gear_dict['warnings'].append(e)
            utils.dry_run.pretend_it_ran(context)

        if ok_to_run:
            # Run the actual command this gear was created for
            result = sp.run(context.gear_dict['command'], 
                        env = context.gear_dict['environ'])
            log.debug(repr(result))

        log.info('Return code: ' + str(result.returncode))

        if result.returncode == 0:
            log.info('Command successfully executed!')

        else:
            log.info('Command failed.')

    except Exception as e:
        context.gear_dict['errors'].append(e)
        log.critical(e)
        log.exception('Unable to execute command.')

    finally:

        # Make archives for result *.html files for easy display on platform
        path = context.gear_dict['output_analysisid_dir'] + \
                                 '/' + context.gear_dict['COMMAND']
        zip_htmls(context, path)

        # Remove all fsaverage* directories
        if not context.config['gear-keep-fsaverage']:
            path = context.gear_dict['output_analysisid_dir'] + \
                                     '/freesurfer/fsaverage*'
            fsavg_dirs = glob.glob(path)
            for fsavg in fsavg_dirs:
                log.info('deleting ' + fsavg)
                shutil.rmtree(fsavg)
        else:
            log.info('Keeping fsaverage directories')

        # save everything in context.gear_dict['output_analysisid_dir']
        # as the main result
        zip_output(context)

        # possibly save ALL intermediate output
        if context.config['gear-save-intermediate-output']:
            zip_all_intermediate_output(context)

        # possibly save intermediate files and folders
        zip_intermediate_selected(context)

        # clean up: remove output that was zipped
        if os.path.exists(context.gear_dict['output_analysisid_dir']):
            if not context.config['gear-keep-output']:

                shutil.rmtree(context.gear_dict['output_analysisid_dir'])
                log.debug('removing output directory "' + 
                          context.gear_dict['output_analysisid_dir'] + '"')

            else:
                log.info('NOT removing output directory "' + 
                          context.gear_dict['output_analysisid_dir'] + '"')

        else:
            log.info('Output directory does not exist so it cannot be removed')

        ret = result.returncode

        if len(context.gear_dict['warnings']) > 0 :
            msg = 'Previous warnings:\n'
            for err in context.gear_dict['warnings']:
                if str(type(err)).split("'")[1] == 'str':
                    # show string
                    msg += '  Warning: ' + str(err) + '\n'
                else:  # show type (of warning) and warning message
                    msg += '  ' + str(type(err)).split("'")[1] + ': ' + str(err) + '\n'
            log.info(msg)

        if len(context.gear_dict['errors']) > 0 :
            msg = 'Previous errors:\n'
            for err in context.gear_dict['errors']:
                if str(type(err)).split("'")[1] == 'str':
                    # show string
                    msg += '  Error msg: ' + str(err) + '\n'
                else:  # show type (of error) and error message
                    msg += '  ' + str(type(err)).split("'")[1] + ': ' + str(err) + '\n'
            log.info(msg)
            ret = 1

        log.info('BIDS App Gear is done.  Returning '+str(ret))
        os.sys.exit(ret)
 

if __name__ == '__main__':

    context = flywheel.GearContext()

    log = initialize(context)

    create_command(context, log)

    set_up_data(context, log)

    execute(context, log)


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
