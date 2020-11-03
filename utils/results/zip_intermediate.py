"""Save files from work/, compressed in output/."""

import logging
import os
import shutil
import subprocess as sp
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

log = logging.getLogger(__name__)


def zip_selected(root_dir, dir_name, output_filename, selected_files, selected_dirs):
    """Zip selected files and directories into output_filename.

    The resulting zip file will unzip into directory dir_name and will maintain the
    original directory structure.  Directory dir_name must be in root_dir.

    Files and directories can be specified by their name alone or by providing a path.
    The path can be partial (including some of the final directories) or full (starting
    with dir_name)

    If specified files or directories are found in multiple places, all will be included
    in the output zip file.

    Args:
        root_dir (Path) path to dir_name
        dir_name (str) name of directory to find selected files/directories
        output_filename (Path) path and name of zip file to save
        selected_files (list) file names or partial paths to files
        selected_dirs (list) dir names or partial paths to dirs
    """

    cwd = Path().cwd()
    os.chdir(root_dir)

    if Path(output_filename).exists():
        Path(output_filename).unlink()

    files_found = []
    dirs_found = []
    with ZipFile(output_filename, "w", ZIP_DEFLATED) as outzip:
        for root, subdirs, files in os.walk(dir_name):
            for fl in files:
                matched = False
                file_path = Path(root) / fl
                if fl in selected_files:
                    matched = True
                    files_found.append(fl)
                else:
                    for sel in selected_files:
                        if file_path.match(sel):
                            matched = True
                            files_found.append(sel)
                if not matched:
                    for sel in selected_dirs:
                        if Path(root).match(sel):
                            dirs_found.append(sel)
                            matched = True
                if matched:
                    log.info("Zipping %s", file_path)
                    outzip.write(file_path)

    for sel in selected_files:
        if sel not in files_found:
            log.warning("Looked for %s but could not find it.", sel)
    for sel in selected_dirs:
        if sel not in dirs_found:
            log.warning("Looked for %s but could not find it.", sel)

    os.chdir(cwd)  # Get back to where you once belonged


def zip_intermediate_selected(context, run_label):
    """Zip the listed files and folders in work/.

    Args:
        context (gear_toolkit.GearToolkitContext): flywheel gear context
        run_label (str) name of run to use in zip file name
    """

    do_find = False
    files = []
    folders = []
    # get list of intermediate files (if any)
    if context.config.get("gear-intermediate-files", None):
        if len(context.config["gear-intermediate-files"]) > 0:
            files = context.config["gear-intermediate-files"].split()
            log.debug(str(files))
            do_find = True

    # get list of intermediate folders (if any)
    if context.config.get("gear-intermediate-folders", None):
        if len(context.config["gear-intermediate-folders"]) > 0:
            folders = context.config["gear-intermediate-folders"].split()
            do_find = True

    if do_find:

        # Name of zip file has <subject> and <analysis>
        analysis_id = context.destination["id"]
        gear_name = context.manifest["name"]
        file_name = f"{gear_name}_work_selected_{run_label}_{analysis_id}.zip"
        dest_zip = os.path.join(context.output_dir, file_name)
        work_dir = Path(context.work_dir)

        log.info('Files and folders will be zipped to "' + dest_zip + '"')
        zip_selected(work_dir.parents[0], work_dir.name, dest_zip, files, folders)

    else:
        log.debug("No files or folders specified in config to zip")


def zip_all_intermediate_output(context, run_label):
    """Zip all intermediate output in the "work/ directory into one archive.

    Args:
        context (gear_toolkit.GearToolkitContext): flywheel gear context
        run_label (str) name of run to use in zip file name
    """

    # Name of zip file has <subject> and <analysis>
    analysis_id = context.destination["id"]
    gear_name = context.manifest["name"]
    file_name = f"{gear_name}_work_{run_label}_{analysis_id}"
    dest_zip = os.path.join(context.output_dir, file_name)

    work_path, work_dir = os.path.split(context.work_dir)
    os.chdir(work_path)

    log.info("Zipping " + work_dir + " directory to " + dest_zip + ".")

    shutil.make_archive(dest_zip, "zip", work_path, work_dir)
