# If you edit this file, please consider updating bids-app-template

import subprocess as sp
import logging


log = logging.getLogger(__name__)


def tree_bids(path, base_name):
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
