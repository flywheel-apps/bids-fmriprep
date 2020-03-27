"""Handle arguments"""

import logging

from .licenses.freesurfer import find_freesurfer_license


log = logging.getLogger(__name__)


def get_inputs_and_args(context):
    """
    Process inputs, contextual values and build a dictionary of
    key:value command-line parameter names:values These will be
    validated and assembled into a command-line below.  
    """

    log.debug('')

    # 1) Process Inputs

    # because one way to pass the license is by an input
    find_freesurfer_license(context, '/opt/freesurfer/license.txt')

    # 2) Process Contextual values
    # e.g. context.matlab_license_code

    # 3) Process Configuration (config, rest of command-line parameters)
    config = context.config
    params = {}
    for key in config.keys():
        if key[:5] == 'gear-':  # Skip any gear- parameters
            continue
        if type(config[key]) == str:
            if config[key]:  # only use non-empty strings
                params[key] = config[key]
        else:
            params[key] = config[key]

    context.gear_dict['param_list'] = params


def validate(context):
    """
    Validate settings of the Parameters constructed.
    Gives warnings for possible settings that could result in bad results.
    Gives errors (and raises exceptions) for settings that are violations 
    """

    param_list = context.gear_dict['param_list']

    log.info('Checking param_list: ' + repr(param_list))

    if 'n_cpus' in param_list:

        cpu_count = context.gear_dict['cpu_count']

        if param_list['n_cpus'] > cpu_count:
            log.warning('n_cpus > number available, using %d', cpu_count)
            param_list['n_cpus'] = cpu_count

        elif param_list['n_cpus'] == 0:
            log.info('n_cpus == 0, using %d (maximum available)', cpu_count)
            param_list['n_cpus'] = cpu_count

    else:  # Default is to use all cpus available
        param_list['n_cpus'] = context.gear_dict['cpu_count']  # zoom zoom


def build_command(context):
    """
    command is a list of prepared commands
    param_list is a dictionary of key:value pairs to be put into the command
    list as such ("-k value" or "--key=value")
    """

    log.debug('')

    command = context.gear_dict['command']

    param_list = context.gear_dict['param_list']

    for key in param_list.keys():
        # Single character command-line parameters are preceded by a single '-'
        if len(key) == 1:
            command.append('-' + key)
            if len(str(param_list[key])) != 0:
                # append it like '-k value'
                command.append(str(param_list[key]))
        # Multi-Character command-line parameters are preceded by a double '--'
        else:
            # If Param is boolean and true include, else exclude
            if type(param_list[key]) == bool:
                if param_list[key]:
                    command.append('--' + key)
            else:
                # If Param not boolean, but without value include without value
                if len(str(param_list[key])) == 0:
                    # append it like '--key'
                    command.append('--' + key)
                else:
                    # check for argparse nargs='*' lists of multiple values so
                    #  append it like '--key val1 val2 ...'
                    if (isinstance(param_list[key], str) and
                       len(param_list[key].split()) > 1):
                        # then it is a list of multiple things:
                        #  e.g. "--modality T1w T2w"
                        command.append('--' + key)
                        for item in param_list[key].split():
                            command.append(item)
                    else:  # single value so append it like '--key=value'
                        command.append('--' + key + '=' + str(param_list[key]))
        if key == 'verbose':
            # handle a 'count' argparse argument where manifest gives
            # enumerated possibilities like v, vv, or vvv
            # e.g. replace "--verbose=vvv' with '-vvv'
            command[-1] = '-' + param_list[key]

    return command
