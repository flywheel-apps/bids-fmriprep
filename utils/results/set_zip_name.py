# If you edit this file, please consider updating bids-app-template

import os
import logging
import subprocess as sp


log = logging.getLogger(__name__)


def set_zip_head(context):
    """Set name for zipped results as
    
           COMMAND_name_destinationID_?.zip

    where:
       COMMAND       = the name of the main command line command
       name          = either project, subject, or session name, which
                       is determined by the run level
       destinationID = the id of the destination container
       ?             = last part added for a particular zip file
    """


    # Set Zip file "name": either project, subject, or session name
    if context.gear_dict['run_level'] == 'project':

        name = context.gear_dict['project_label_safe']

    elif context.gear_dict['run_level'] == 'subject':
    
        name = context.gear_dict['subject_code_safe'] 

    elif context.gear_dict['run_level'] == 'session':

        name = context.gear_dict['session_label_safe']

    context.gear_dict['zip_head'] = context.gear_dict['COMMAND'] +\
        '_' + name + '_' + context.destination['id']


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
