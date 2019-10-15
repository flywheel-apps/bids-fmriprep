# If you edit this file, please consider updating bids-app-template

import logging
import subprocess as sp


log = logging.getLogger(__name__)


def zip_it_zip_it_good(context, name):
    """ Compress html file into an appropriately named archive file
        *.html.zip files are automatically shown in another tab in the browser """

    cmd = 'zip -q ' + name + '.zip index.html'
    log.debug(' creating viewable archive "' + name + '.zip"')
    result = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf-8')
    if result.returncode != 0:
        log.info(' Problem running ' + cmd)
        log.info(' return code: ' + str(result.returncode))
        log.info(' ' + cmd.split()[0] + ' output\n' + str(result.stdout))
    else:
        log.debug(' return code: ' + str(result.returncode))
        log.debug(' ' + cmd.split()[0] + ' output\n' + str(result.stdout))


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
