"""Compress HTML files."""

import datetime
import glob
import logging
import os
import subprocess as sp
from pathlib import Path

FWV0 = Path.cwd()
log = logging.getLogger(__name__)


def zip_it_zip_it_good(output_dir, destination_id, name, path):
    """Compress html file into an appropriately named archive file *.html.zip
    files are automatically shown in another tab in the browser. These are
    saved at the top level of the output folder."""

    name_no_html = name[:-5]  # remove ".html" from end

    dest_zip = os.path.join(
        output_dir, name_no_html + "_" + destination_id + ".html.zip"
    )

    log.debug('Creating viewable archive "' + dest_zip + '"')

    command = ["zip", "-q", "-r", dest_zip, "index.html"]

    # find all directories called 'figures' and add them to the archive
    for root, dirs, files in os.walk(path):
        for name in dirs:
            if name == "figures":
                # path = "/".join(os.path.join(root, name).split("/")[6:])
                # command.append(path)
                figures_path = root.split("/")[-1] + "/figures"
                command.append(figures_path)
                log.info(f"including {figures_path}")

    # log command as a string separated by spaces
    log.debug(f"pwd = %s", Path.cwd())
    log.debug(" ".join(command))

    result = sp.run(command, check=True)


def zip_htmls(output_dir, destination_id, path):
    """Zip all .html files at the given path so they can be displayed
    on the Flywheel platform.
    Each html file must be converted into an archive individually:
      rename each to be "index.html", then create a zip archive from it.
    """

    log.info("Creating viewable archives for all html files")

    if os.path.exists(path):

        log.debug("Found path: " + str(path))

        os.chdir(path)

        html_files = glob.glob("*.html")

        if len(html_files) > 0:

            # if there is an index.html, do it first and re-name it for safe
            # keeping
            save_name = ""
            if os.path.exists("index.html"):
                log.info("Found index.html")
                zip_it_zip_it_good(output_dir, destination_id, "index.html", path)

                now = datetime.datetime.now()
                save_name = now.strftime("%Y-%m-%d_%H-%M-%S") + "_index.html"
                os.rename("index.html", save_name)

                html_files.remove("index.html")  # don't do this one later

            for h_file in html_files:
                log.info("Found %s", h_file)
                os.rename(h_file, "index.html")
                zip_it_zip_it_good(output_dir, destination_id, h_file, path)
                os.rename("index.html", h_file)

            # reestore if necessary
            if save_name != "":
                os.rename(save_name, "index.html")

        else:
            log.warning("No *.html files at " + str(path))

    else:

        log.error("Path NOT found: " + str(path))

    os.chdir(FWV0)
