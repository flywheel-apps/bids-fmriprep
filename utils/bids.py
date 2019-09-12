# If you edit this file, please consider updating bids-app-template
import os, os.path as op
import subprocess as sp
import json
import pprint

def download(context):
    """ Download all files from the session in BIDS format
        bids_path will point to the local BIDS folder
        This creates a simiple dataset_description.json if
        one did not get downloaded.
    """

    # the usual BIDS path:
    bids_path = op.join(context.work_dir, 'bids')

    # If BIDS was already downloaded, don't do it again
    # (this saves time when developing locally)
    if not op.isdir(bids_path):

        bids_path = context.download_session_bids(target_dir=bids_path)
        # Use the following command instead (after core is updated with a fix
        # for it) because it will return the existing dataset_description.json
        # file and does not download scans that don't need to be considered.
        # bids_path = context.download_project_bids(folders=['anat', 'func'])

        # Another way to get this file if there is an input is:
        #acq = fw.get_acquisition(context.get_input(<input key>)['hierarchy']['id'])
        #session = fw.get_session(acq.session)
        #project = fw.get_project(session.parents.project)
        #dataset_description = project.info.get(['BIDS'])

        # make sure dataset_description.json exists
        # Is there a way to download the dataset_description.json file from the 
        # platform instead of creating a generic stub?
        required_file = bids_path + '/dataset_description.json'
        if not op.exists(required_file):
            context.log.info('Creating missing '+required_file+'.')
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
            context.log.info(required_file+' exists.')

        context.log.info('BIDS was downloaded into '+bids_path)

    else:
        context.log.info('Using existing BIDS path '+bids_path)
    
    context.gear_dict['bids_path'] = bids_path


def run_validation(context):
    """ Run BIDS Validator on bids_path
        Install BIDS Validator into container with: 
            RUN npm install -g bids-validator
        This prints a summary of files that are valid,
        and then lists errors and warnings.
        Then it exits if gear-abort-on-bids-error is set and
        if there are any errors.
        The config MUST contain both of these:
            gear-run-bids-validation
            gear-abort-on-bids-error
    """
    config = context.config
    bids_path = context.gear_dict['bids_path']
    environ = context.gear_dict['environ']

    if config['gear-run-bids-validation']:

        command = ['bids-validator', '--verbose', '--json', bids_path]
        context.log.info('Command:' + ' '.join(command))

        out_path = "work/validator.output.txt"
        with open(out_path, "w") as f:
            result = sp.run(command, stdout=f, stderr=sp.PIPE,
                            universal_newlines=True, env=environ)

        context.log.info(command[0]+' return code: ' + str(result.returncode))

        if result.stderr:
            context.log.error(result.stderr)

        with open(out_path) as jfp:
            bids_output = json.load(jfp)

        # show summary of valid BIDS stuff
        context.log.info('bids-validator results:\n\nValid BIDS files summary:\n' +
                 pprint.pformat(bids_output['summary'], indent=8) + '\n')

        num_bids_errors = len(bids_output['issues']['errors'])

        # show all errors
        for err in bids_output['issues']['errors']:
            err_msg = err['reason'] + '\n'
            for ff in err['files']:
                if ff["file"]:
                    err_msg += '       ' + ff["file"]["relativePath"] + '\n'
            context.log.error(err_msg)

        # show all warnings
        for warn in bids_output['issues']['warnings']:
            warn_msg = warn['reason'] + '\n'
            for ff in warn['files']:
                if ff["file"]:
                    warn_msg += '       ' + ff["file"]["relativePath"] + '\n'
            context.log.warning(warn_msg)

        if config['gear-abort-on-bids-error'] and num_bids_errors > 0:
            raise Exception(' ' + str(num_bids_errors) + ' BIDS validation errors ' +
                         'were detected: NOT running.')
            # raising Exception instead of exiting.... exterior "try"-block 
            # catches these


def tree(path, base_name):
    """ Write `tree` output as html file for the given path
        ".html" will be appended to base_name to create the
        file name to use for the result.
    """

    command = ['tree', '--charset=utf-8', path]
    result = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE,
                    universal_newlines=True)

    html1 = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n' + \
            '<html>\n' + \
            '  <head>\n' + \
            '    <meta http-equiv="content-type" content="text/html; charset=UTF-8">\n' + \
            '    <title>tree ' + path + '</title>\n' + \
            '  </head>\n' + \
            '  <body>\n' + \
            '<pre>\n'

    html2 = '</pre>\n' + \
            '    </blockquote>\n' + \
            '  </body>\n' + \
            '</html>\n'

    # put all of that text into the actual file
    with open(base_name + ".html", "w") as html_file:
        html_file.write(html1)
        for line in result.stdout.split('\n'):
            html_file.write(line+'\n')
        html_file.write(html2)

# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
