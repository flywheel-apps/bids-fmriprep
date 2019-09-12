#!/usr/bin/env python3

import json
import os, os.path as op
import subprocess as sp
import logging
import psutil

import flywheel

# GearContext takes care of most of these variables
# from utils.G import *
from utils import args, bids, results
from utils.log import get_custom_logger

if __name__ == '__main__':
    # Instantiate the Gear Context
    context = flywheel.GearContext()
    # Get Custom Logger and set attributes
    context.log = get_custom_logger('[flywheel/bids-fmriprep]')
    context.log.setLevel(getattr(logging, context.config['gear-log-level']))

    # Instantiate custom gear dictionary to hold "gear global" info
    context.gear_dict = {}

    # editme: optional feature
    # f-strings (e.g. f'string {variable}') are introduced in Python3.6
    # for Python3.5 use ('string {}'.format(variable))
    context.log.debug('psutil.cpu_count()= '+str(psutil.cpu_count()))
    context.log.debug('psutil.virtual_memory().total= {:4.1f} GiB'.format(
                      psutil.virtual_memory().total / (1024 ** 3)))
    context.log.debug('psutil.virtual_memory().available= {:4.1f} GiB'.format(
                      psutil.virtual_memory().available / (1024 ** 3)))

    # grab environment for gear
    with open('/tmp/gear_environ.json', 'r') as f:
        environ = json.load(f)
        context.gear_dict['environ'] = environ

    try:
        # editme: for debugging:
        if context.destination['id'] == 'aex':
            # give it the tome session
            context.destination['id']='5d2761383289d60037e8b180'

        # Download bids for the current session
        bids.download(context)

        # editme: optional feature
        # Save bids file hierarchy `tree` output in .html file
        bids_path = context.gear_dict['bids_path']
        html_file = 'output/bids_tree'
        bids.tree(bids_path, html_file)
        context.log.info('Wrote tree("' + bids_path + '") output into html file "' +
                         html_file + '.html')

        # editme: optional feature, but recommended!
        # Validate Bids file heirarchy
        # Bids validation on a phantom tree may be occuring soon
        bids.run_validation(context)

    except Exception as e:
        context.log.critical(e,)
        context.log.exception('Error in BIDS download and validation.',)
        os.sys.exit(1)

    try:
        # editme: optional feature
        # Create working output directory with session label as name
        args.make_session_directory(context)

        # editme: this is the actual command to run the gear
        context.gear_dict['command'] = ['echo']
        context.gear_dict['command'].append(
            op.join(context.work_dir,context.gear_dict['session_label'])
        )
        # Build a parameter dictionary specific for COMMAND
        args.build(context)

        # Validate the command parameter dictionary
        # Raises Exception on fail
        args.validate(context)

        # Build command-line string for subprocess and execute
        args.execute(context)
        
        context.log.info(' Command successfully executed!')
        os.sys.exit(0)

    except Exception as e:
        context.log.critical(e,)
        context.log.exception('Unable to execute command.')
        os.sys.exit(1)

    finally:
        # editme: optional feature
        # Cleanup, move all results to the output directory
        results.zip_htmls(context)

        # possibly save ALL intermediate output
        if context.config['gear-save-all-output']:
            results.zip_output(context)


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
