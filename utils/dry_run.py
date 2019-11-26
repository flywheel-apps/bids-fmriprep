# If you edit this file, please consider updating bids-app-template

import os
import logging
from pathlib import Path
import sys


log = logging.getLogger(__name__)


def pretend_it_ran(context):
    """
    Make some output like fmriprep would have done only fake.
    """


    # Work diredtory
    path = 'work/'

    log.info('Creating fake output in ' + path)

    files = [path + 'fmriprep_wf/d3.js',
             path + 'reportlets/fmriprep/sub-TOME3024/anat/' + \
             'sub-TOME3024_desc-about_T1w.html']

    for ff in files:
        if os.path.exists(ff):
            log.debug('Exists: ' + ff)
        else:
            log.debug('Creating: ' + ff)
            dir_name = os.path.dirname(ff)
            os.makedirs(dir_name)
            Path(ff).touch(mode=0o777, exist_ok=True)


    # Output diredtory
    path = 'output/' + context.destination['id'] + '/'

    log.info('Creating fake output in ' + path)

    files = [path + 'fmriprep/logs/CITATION.md',
             path + 'fmriprep/sub-TOME3024/ses-Session2/anat/' + \
             'sub-TOME3024_ses-Session2_acq-MPR_from-orig_to-T1w_mode-image_xfm.txt',
             path + 'freesurfer/fsaverage/mri/subcort.prob.log']

    for ff in files:
        if os.path.exists(ff):
            log.debug('Exists: ' + ff)
        else:
            log.debug('Creating: ' + ff)
            dir_name = os.path.dirname(ff)
            os.makedirs(dir_name)
            Path(ff).touch(mode=0o777, exist_ok=True)

    html = """<html>
    <head> 
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>sub-TOME3024</title>
    </head>
    <body>
    <h1>sub-TOME3024</h1>
    <p>This is a test html file.&nbsp; How do you love it?<br>
    </p>
    </body>
    </html>"""
    ff = path + 'fmriprep/sub-TOME3024.html'
    with open(ff,'w') as fp:
        fp.write(html)
    log.debug('Creating: ' + ff)

# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
