# If you edit this file, please consider updating bids-app-template
import datetime
import glob
import os, os.path as op
import subprocess as sp


def zip_it_zip_it_good(context, name):
    """ Compress html file into an appropriately named archive file
        *.html.zip files are automatically shown in another tab in the browser """

    cmd = 'zip -q ' + name + '.zip index.html'
    context.log.debug(' creating viewable archive "' + name + '.zip"')
    result = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf-8')
    if result.returncode != 0:
        context.log.info(' Problem running ' + cmd)
        context.log.info(' return code: ' + str(result.returncode))
        context.log.info(' ' + cmd.split()[0] + ' output\n' + str(result.stdout))
    else:
        context.log.debug(' return code: ' + str(result.returncode))
        context.log.debug(' ' + cmd.split()[0] + ' output\n' + str(result.stdout))


def zip_htmls(context):
    """ Since zip_all_html() doesn't work, each html file must be
        converted into an archive individually.
        For each html file, rename it to be "index.html", then create a zip
        archive from it.
    """

    context.log.info(' Creating viewable archives for all html files')
    os.chdir(context.output_dir)

    html_files = glob.glob('*.html')

    # if there is an index.html, do it first and re-name it for safe keeping
    save_name = ''
    if op.exists('index.html'):
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


def zip_all_htmls(context):
    """ If there is no index.html, construct one that links to all
        html files.
        Then make a zip archive that has all html files.

        NOTE: Creating a single html file with links to all html files
        DOES NOT WORK because the server won't serve the pages at the links.
        So do not use this function unless something changes.
    """

    if not op.exists('index.html'):  # create one if it does not exist

        context.log.info(' Creating index.html')
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
    context.log.info(' creating viewable html archive "' + cmd + '"')
    result = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf-8')
    if result.returncode != 0:
        context.log.info(' return code: ' + str(result.returncode))
        context.log.info(' ' + cmd.split()[0] + ' output\n' + str(result.stdout))


def zip_output(context):
    # Cleanup, create manifest, create zipped results,
    # move all results to the output directory
    # This executes regardless of errors or exit status,
    os.chdir(context.work_dir)
    # If the output/result.anat path exists, zip regardless of exit status
    # Clean input_file_basename to lack esc chars and extension info

    # Grab Session label
    session_label = context.gear_dict['session_label']
    dest_zip = op.join(context.output_dir,session_label + '.zip')

    if op.exists(op.join(context.work_dir,session_label)):
        context.log.info(
            'Zipping ' + session_label + ' directory to ' + dest_zip + '.'
        )
        # For results with a large number of files, provide a manifest.
        # Capture the stdout/stderr in a file handle or for logging.
        manifest = op.join(
            context.output_dir, session_label + '_output_manifest.txt'
        )
        command0 = ['tree', '-shD', '-D', session_label]
        with open(manifest, 'w') as f:
            result0 = sp.run(command0, stdout = f)
        command1 = ['zip', '-r', dest_zip, session_label]
        result1 = sp.run(command1, stdout=sp.PIPE, stderr=sp.PIPE)
    else:
        context.log.info(
            'No results directory, ' + \
            op.join(context.work_dir,session_label) + \
            ', to zip.'
        )

# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
