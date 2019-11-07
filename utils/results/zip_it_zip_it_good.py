# If you edit this file, please consider updating bids-app-template

import logging
import subprocess as sp


log = logging.getLogger(__name__)


def zip_it_zip_it_good(context, name):
    """ Compress html file into an appropriately named archive file
        *.html.zip files are automatically shown in another tab in the browser """


    log.info('Creating viewable archive "' + name + '.zip"')

    command = ['zip', '-q', name + '.zip', 'index.html']
    result = sp.run(command, check=True)


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
