# If you edit this file, please consider updating bids-app-template

import subprocess as sp
import logging
import json
import pprint


log = logging.getLogger(__name__)


def validate_bids(context):
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

    log.debug('')

    config = context.config
    bids_path = context.gear_dict['bids_path']
    environ = context.gear_dict['environ']

    if config['gear-run-bids-validation']:

        command = ['bids-validator', '--verbose', '--json', bids_path]
        log.info('Command: ' + ' '.join(command))

        out_path = "work/validator.output.txt"
        with open(out_path, "w") as f:
            result = sp.run(command, stdout=f, stderr=sp.PIPE,
                            universal_newlines=True, env=environ)

        log.info(command[0]+' return code: ' + str(result.returncode))

        if result.stderr:
            log.error(result.stderr)

        with open(out_path) as jfp:
            bids_output = json.load(jfp)

        try:
            # show summary of valid BIDS stuff
            log.info('bids-validator results:\n\nValid BIDS files summary:\n' +
                     pprint.pformat(bids_output['summary'], indent=8) + '\n')

            num_bids_errors = len(bids_output['issues']['errors'])

            # show all errors
            for err in bids_output['issues']['errors']:
                err_msg = err['reason'] + '\n'
                for ff in err['files']:
                    if ff["file"]:
                        err_msg += '       ' + ff["file"]["relativePath"] + '\n'
                log.error(err_msg)

            # show all warnings
            for warn in bids_output['issues']['warnings']:
                warn_msg = warn['reason'] + '\n'
                for ff in warn['files']:
                    if ff["file"]:
                        warn_msg += '       ' + ff["file"]["relativePath"] + '\n'
                log.warning(warn_msg)

        except KeyError as e:
            num_bids_errors = 1
            msg = 'KeyError: bids-validator result missing ' + str(repr(e))
            log.critical(msg)
            context.gear_dict['errors'].append(msg)

        if num_bids_errors > 0:

            msg = 'bids-validator detected errors'
            log.error(msg)
            context.gear_dict['errors'].append(msg)

            if config['gear-abort-on-bids-error'] and num_bids_errors > 0:
                raise Exception(' ' + str(num_bids_errors) + ' BIDS validation errors ' +
                             'were detected: NOT running.')
                # raising Exception instead of exiting.... exterior "try"-block 
                # catches these


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
