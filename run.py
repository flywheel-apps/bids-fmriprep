#!/usr/bin/env python3
""" Run the gear: set up for and call command-line code """

import json
import os, os.path as op
import subprocess as sp
import sys
import logging
import psutil

import flywheel

# GearContext takes care of most of these variables
# from utils.G import *
from utils import args, bids, results


if __name__ == '__main__':

    log = logging.getLogger('[flywheel/bids-fmriprep]')

    # Instantiate the Gear Context
    context = flywheel.GearContext()
    context.init_logging(context.config['gear-log-level'])

    log.setLevel(context.config['gear-log-level'])
    log.info('log level is ' + context.config['gear-log-level'])

    # remove the standard handler so the format can be changed
    logging.root.removeHandler(context.log.root.handlers[0])
    # Timestamps with logging assist debugging algorithms
    # With long execution times
    handler = logging.StreamHandler(stream=sys.stdout)
    format = '%(asctime)s %(levelname)8s %(name)-8s - %(message)s'
    formatter = logging.Formatter(
                fmt=format,
                datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    # replace root log handler
    context.log.root.addHandler(handler)

    context.log_config() # not configuring the log but logging the config

    # Instantiate custom gear dictionary to hold "gear global" info
    context.gear_dict = {}

    # editme: optional feature
    # f-strings (e.g. f'string {variable}') are introduced in Python3.6
    # for Python3.5 use ('string {}'.format(variable))
    #log.debug('psutil.cpu_count()= '+str(psutil.cpu_count()))
    #log.debug('psutil.virtual_memory().total= {:4.1f} GiB'.format(
    #                  psutil.virtual_memory().total / (1024 ** 3)))
    #log.debug('psutil.virtual_memory().available= {:4.1f} GiB'.format(
    #                  psutil.virtual_memory().available / (1024 ** 3)))

    # grab environment for gear
    with open('/tmp/gear_environ.json', 'r') as f:
        environ = json.load(f)
        context.gear_dict['environ'] = environ

    # Call this if args.make_session_directory() or results.zip_output() is
    # called later because they expect context.gear_dict['session_label']
    args.set_session_label(context)

    try:

        # Set the actual command to run the gear:
        context.gear_dict['command'] = ['fmriprep']

        # Build a parameter dictionary specific for COMMAND
        args.build(context)

        # Validate the command parameter dictionary - make sure everything is 
        # ready to run so errors will appear before launching the actual gear 
        # code.  Raises Exception on fail
        args.validate(context)

    except Exception as e:
        log.critical(e,)
        log.exception('Error in parameter specification.',)
        os.sys.exit(1)

    try:

        # Download bids for the current session
        bids.download(context)

        # editme: optional feature
        # Save bids file hierarchy `tree` output in .html file
        bids_path = context.gear_dict['bids_path']
        html_file = 'output/bids_tree'
        bids.tree(bids_path, html_file)
        log.info('Wrote tree("' + bids_path + '") output into html file "' +
                         html_file + '.html')

        # editme: optional feature, but recommended!
        # Validate Bids file heirarchy
        # Bids validation on a phantom tree may be occuring soon
        bids.run_validation(context)

    except Exception as e:
        log.critical(e,)
        log.exception('Error in BIDS download and validation.',)
        os.sys.exit(1)

    try:

        # Build command-line string for subprocess and execute
        result = args.execute(context)

        log.info('Return code: ' + str(result.returncode))
        log.info('stdout = ' + str(result.stdout))

        if result.returncode == 0:
            log.info('Command successfully executed!')

        else:
            log.error('stderr = ' + str(result.stderr))
            log.info('Command failed.')

    except Exception as e:
        log.critical(e,)
        log.exception('Unable to execute command.')
        os.sys.exit(1)

    finally:

        # possibly save ALL intermediate output
        if context.config['gear-save-all-output']:
            results.zip_output(context)

        try:
            ret = result.returncode
        except NameError:
            ret = 1

        log.info('BIDS App Gear is done.')
        os.sys.exit(ret)


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
