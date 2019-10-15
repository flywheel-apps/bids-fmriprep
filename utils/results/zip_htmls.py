# If you edit this file, please consider updating bids-app-template

import datetime
import glob
import os
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


def zip_htmls(context):
    """ Since zip_all_html() doesn't work, each html file must be
        converted into an archive individually.
        For each html file, rename it to be "index.html", then create a zip
        archive from it.
    """

    log.info(' Creating viewable archives for all html files')
    os.chdir(context.output_dir)

    html_files = glob.glob('*.html')

    # if there is an index.html, do it first and re-name it for safe keeping
    save_name = ''
    if os.path.exists('index.html'):
        zip_it_zip_it_good(context,'index.html')

        now = datetime.datetime.now()
        save_name = now.strftime("%Y-%m-%d_%H-%M-%S") + '_index.html'
        os.rename('index.html', save_name)

        html_files.remove('index.html')  # don't do this one later

    for h_file in html_files:
        os.rename(h_file, 'index.html')
        zip_it_zip_it_good(context,h_file)
        os.rename('index.html', h_file)

    # reestore if necessary
    if save_name != '':
        os.rename(save_name, 'index.html')


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
