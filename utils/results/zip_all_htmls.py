# If you edit this file, please consider updating bids-app-template

import glob
import os
import logging
import subprocess as sp


log = logging.getLogger(__name__)


def zip_all_htmls(context):
    """ If there is no index.html, construct one that links to all
        html files.
        Then make a zip archive that has all html files.

        NOTE: Creating a single html file with links to all html files
        DOES NOT WORK because the server won't serve the pages at the links.
        So do not use this function unless something changes.
    """

    if not os.path.exists('index.html'):  # create one if it does not exist

        log.info(' Creating index.html')
        os.chdir(context.output_dir)

        # the first part of index.html
        html1 = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n' + \
                '<html>\n' + \
                '  <head>\n' + \
                '    <meta http-equiv="content-type" content="text/html; charset=UTF-8">\n' + \
                '    <title>Command Output</title>\n' + \
                '  </head>\n' + \
                '  <body>\n' + \
                '    <b>Command Output</b><br>\n' + \
                '    <br>\n' + \
                '    <tt>\n'

        # get a list of all html files
        html_files = glob.glob('*.html')

        lines = []
        for h_file in html_files:
            # create a link to that h_file file
            s = '    <a href="./' + h_file + '">' + h_file[:-5] + '</a><br>\n'
            lines.append(s)

        # The final part of index.html
        html2 = '    <br>\n' + \
                '    </tt>\n' + \
                '  </body>\n' + \
                '</html>\n'

        # put all of that text into the actual file
        with open("index.html", "w") as text_file:
            text_file.write(html1)
            for line in lines:
                text_file.write(line)
            text_file.write(html2)

    # compress everything into an appropriately named archive file
    # *.html.zip file are automatically shown in another tab in the browser
    cmd = 'zip -q Command.html.zip *.html'
    log.info(' creating viewable html archive "' + cmd + '"')
    result = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf-8')
    if result.returncode != 0:
        log.info(' return code: ' + str(result.returncode))
        log.info(' ' + cmd.split()[0] + ' output\n' + str(result.stdout))


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
