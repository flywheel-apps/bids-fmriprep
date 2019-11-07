#!/usr/bin/env python3
""" Run the gear: set up for and call command-line code """

import json
import os
import subprocess as sp
import sys
import shutil

import flywheel
from utils import args
from utils.bids.download_bids import *
from utils.bids.validate_bids import *
from utils.fly.custom_log import *
from utils.fly.load_manifest_json import *
from utils.results.zip_output import *
from utils.results.zip_htmls import *
from utils.results.zip_intermediate import zip_all_intermediate_output
from utils.results.zip_intermediate import zip_intermediate_selected
import utils.dry_run


def initialize(context):

    # Add manifest.json as the manifest_json attribute
    setattr(context, 'manifest_json', load_manifest_json())

    log = custom_log(context)

    context.log_config() # not configuring the log but logging the config

    # Instantiate custom gear dictionary to hold "gear global" info
    context.gear_dict = {}

    # Get subject code from destination
    fw = context.client
    dest_container = fw.get(context.destination['id'])
    subject_id = dest_container.parents.subject
    subject = fw.get(subject_id)
    context.gear_dict['subject'] = subject.code

    # the usual BIDS path:
    bids_path = os.path.join(context.work_dir, 'bids')
    context.gear_dict['bids_path'] = bids_path

    # in the output/ directory, add extra analysis_id directory name for easy
    #  zipping of final outputs to return.
    context.gear_dict['output_analysisid_dir'] = \
        context.output_dir + '/' + context.destination['id']

    # Keep a list of errors to print all in one place at end
    context.gear_dict['errors'] = []

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
        command = ['fmriprep']

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
        # editme: add kwargs to limit what is downloaded
        # bool src_data: Whether or not to include src data (e.g. dicoms) default: False
        # list subjects: The list of subjects to include (via subject code) otherwise all subjects
        # list sessions: The list of sessions to include (via session label) otherwise all sessions
        # list folders: The list of folders to include (otherwise all folders) e.g. ['anat', 'func']
        # **kwargs: Additional arguments to pass to download_bids_dir
        download_bids(context, subjects=[context.gear_dict['subject']],folders=['anat', 'func', 'fmap'])

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

        if context.config['gear-dry-run']:
            ok_to_run = False
            result = sp.CompletedProcess
            result.returncode = 1
            e = 'gear-dry-run is set: Command was NOT run.'
            log.info(e)
            context.gear_dict['errors'].append(e)
            utils.dry_run.pretend_it_ran(context)

        if ok_to_run:
            # Run the actual command this gear was created for
            result = sp.run(context.gear_dict['command'], 
                        env = context.gear_dict['environ'])

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
        zip_htmls(context)

        zip_output(context)

        # possibly save ALL intermediate output
        if context.config['gear-save-intermediate-output']:
            zip_all_intermediate_output(context)

        # possibly save intermediate files and folders
        zip_intermediate_selected(context)

        # clean up: removed output that was zipped
        shutil.rmtree(context.gear_dict['output_analysisid_dir'])

        ret = result.returncode

        if len(context.gear_dict['errors']) > 0 :
            msg = 'Previous errors:\n'
            for err in context.gear_dict['errors']:
                if str(type(err)).split("'")[1] == 'str':
                    msg += '  Error msg: ' + str(err) + '\n'
                else:
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
