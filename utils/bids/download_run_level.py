#!/usr/bin/env python3
"""A robust template for accessing BIDS formatted data."""

import json
import logging
import shutil
from pathlib import Path

from flywheel import ApiException
from flywheel_bids.export_bids import download_bids_dir
from flywheel_bids.supporting_files.errors import BIDSExportError

from .tree import tree_bids
from .validate import validate_bids

log = logging.getLogger(__name__)

DATASET_DESCRIPTION = {
    "Acknowledgements": "",
    "Authors": [],
    "BIDSVersion": "1.2.0",
    "DatasetDOI": "",
    "Funding": [],
    "HowToAcknowledge": "",
    "License": "",
    "Name": "tome",
    "ReferencesAndLinks": [],
    "template": "project",
}


def fix_dataset_description(bids_path):
    """Make sure dataset_description.json exists and that "Funding" is a list.

    If these are not true, BIDS validation will fail.

    The flywheel bids template had (or has, unless it has been fixed), the
    default dataset_description.json file with "Funding" as an empty string.

    But the BIDS standard requires "Funding" and a list so the validator
    will error out and prevent BIDS Apps from running.

    This fixes that by checking to make sure it is a list and if not,
    converting it to a list and then writing the file back out.

    Args:
        bids_path (path): path to bids formatted data.

    Note:
        If dataset_description.json does not exist, it will be created
    """

    validator_file = bids_path / "dataset_description.json"

    need_to_write = False

    if validator_file.exists():

        with open(validator_file) as json_file:

            data = json.load(json_file)

            log.info("type of Funding is: %s", str(type(data["Funding"])))

            if not isinstance(data["Funding"], list):

                log.warning('data["Funding"] is not a list')
                data["Funding"] = list(data["Funding"])
                log.info("changed it to: %s", str(type(data["Funding"])))

                need_to_write = True

    else:
        log.info("Creating default dataset_description.json file")
        data = DATASET_DESCRIPTION
        need_to_write = True

    if need_to_write:
        with open(validator_file, "w") as outfile:
            json.dump(data, outfile)


def download_bids_for_runlevel(
    gtk_context,
    hierarchy,
    tree=False,
    tree_title=None,
    src_data=False,
    folders=[],
    dry_run=False,
    do_validate_bids=True,
):
    """Figure out run level, download BIDS, validate BIDS, tree work/bids.

    Args:
        gtk_context (gear_toolkit.GearToolkitContext): flywheel gear context
        hierarchy (dict): containing the run_level and labels for the
            run_label, group, project, subject, session, and
            acquisition.
        tree (boolean): create HTML page in output showing 'tree' of bids data
        tree_title (str): Title to put in HTML file that shows the tree
        src_data (boolean): download source data (dicoms) as well
        folders (list): only include the listed folders, if empty include all
        dry_run (boolean): don't actually download data if True
        do_validate_bids (boolean): run bids-validator after downloading bids data

    Returns:
        err_code (int): tells a bit about the error:
            0    - no error
            1..9 - error code returned by bids validator
            10   - BIDS validation errors were detected
            11   - the validator could not be run
            12   - TypeError while analyzing validator output
            20   - running at wrong level
            21   - BIDSExportError
            22   - validator exception
            23   - attempt to download unknown acquisition
            24   - destination does not exist
            25   - download_bids_dir() ApiException
            26   - no BIDS data was downloaded

    Note: information on BIDS "folders" (used to limit what is downloaded)
    can be found at https://bids-specification.readthedocs.io/en/stable/99-appendices/04-entity-table.html.
    """

    extra_tree_text = ""  # Text to be added to the end of the tree HTML file

    run_level = hierarchy["run_level"]

    # Show the complete destination hierarchy in the tree html output for
    # clarity
    extra_tree_text += f"run_level is {run_level}\n"
    for key, val in hierarchy.items():
        extra_tree_text += f"  {key:<18}: {val}\n"
    extra_tree_text += f'  {"folders":<18}: {folders}\n'
    if src_data:
        extra_tree_text += f'  {"source data?":<18}: downloaded\n'
    else:
        extra_tree_text += f'  {"source data?":<18}: not downloaded\n'
    if dry_run:
        extra_tree_text += f'  {"dry run?":<18}: Yes\n'
    else:
        extra_tree_text += f'  {"dry run?":<18}: No\n'
    extra_tree_text += "\n"

    err_code = 0  # assume no error

    if run_level == "no_destination":
        msg = "Destination does not exist."
        log.critical(msg)
        extra_tree_text += f"ERROR: {msg}\n"
        bids_path = None
        err_code = 24  # destination does not exist

    else:

        # The destination is usually an analysis.  If not, say what's going on
        if gtk_context.destination["type"] == "analysis":
            pass

        elif gtk_context.destination["type"] == "acquisition":
            log.info("Destination is acquisition, changing run_level to " "acquisition")
            acquisition = gtk_context.client.get_acquisition(
                gtk_context.destination["id"]
            )
            hierarchy["acquisition_label"] = acquisition.label
            extra_tree_text += (
                f'  {"acquisition_label":<18}: changed to ' + f"{acquisition.label}\n\n"
            )
            run_level = "acquisition"

        else:
            log.info(
                'The destination "%s" is not an analysis or acquisition.',
                gtk_context.destination["type"],
            )

        try:  # download BIDS data for the proper run level

            if src_data:
                log.info("Downloading source data.")
            else:
                log.info("Not downloading source data.")

            if dry_run:
                log.info("Dry run is set.  No data will be downloaded.")
            else:
                log.info("Dry run is NOT set.  Data WILL be downloaded.")

            if len(folders) > 0:
                log.info("Downloading BIDS only in folders: %s", folders)
            else:
                log.info("Downloading BIDS data in all folders.")

            bids_dir = Path(gtk_context.work_dir) / "bids"

            if run_level in ["project", "subject", "session"]:

                log.info(
                    'Downloading BIDS for %s "%s"',
                    hierarchy["run_level"],
                    hierarchy["run_label"],
                )

                if Path(bids_dir).exists():  # This happens during testing
                    bids_path = bids_dir
                    log.info(f"Not actually downloading it because {bids_dir} exists")
                else:

                    subjects = [
                        v
                        for k, v in hierarchy.items()
                        if "subject" in k and v is not None
                    ]
                    sessions = [
                        v
                        for k, v in hierarchy.items()
                        if "session" in k and v is not None
                    ]

                    bids_path = gtk_context.download_project_bids(
                        src_data=src_data,
                        folders=folders,
                        dry_run=dry_run,
                        subjects=subjects,
                        sessions=sessions,
                    )

            elif run_level == "acquisition":

                if hierarchy["acquisition_label"] == "unknown acquisition":
                    msg = (
                        'Cannot download BIDS for acquisition "'
                        + hierarchy["acquisition_label"]
                        + '"'
                    )
                    log.critical(msg)
                    extra_tree_text += f"ERROR: {msg}\n"
                    bids_path = None
                    err_code = 23  # attempt to download unknown acquisition

                else:
                    log.info(
                        'Downloading BIDS for acquisition "%s"',
                        hierarchy["acquisition_label"],
                    )

                    bids_path = bids_dir
                    if Path(bids_dir).exists():
                        log.info(
                            "Not actually downloading it because " f"{bids_dir} exists"
                        )
                    else:
                        # only download acquisition data
                        download_bids_dir(
                            gtk_context.client,
                            gtk_context.destination["id"],
                            "acquisition",
                            bids_dir,
                            src_data=src_data,
                            folders=folders,
                            dry_run=dry_run,
                        )

            else:
                msg = (
                    "This job is not being run at the project, subject, "
                    + f"session or acquisition level. run_level = {run_level}"
                )
                log.critical(msg, exc_info=True)
                extra_tree_text += f"ERROR: {msg}\n"
                bids_path = None
                err_code = 20

        except BIDSExportError as bids_err:
            log.critical(bids_err, exc_info=True)
            extra_tree_text += f"{bids_err}\n"
            bids_path = None
            err_code = 21

        except ApiException as err:
            log.exception(err, exc_info=True)
            extra_tree_text += f"EXCEPTION: {err}\n"
            bids_path = None
            err_code = 25  # download_bids_dir() ApiException

    if bids_path:  # then the string was set so check if the directory exists

        if Path(bids_path).exists():
            log.info("Found BIDS path %s", str(bids_path))

            # Make sure "Funding" is a list or validation will fail
            fix_dataset_description(bids_path)

            # now that work/bids/ exists, copy in the ignore file
            bidsignore_list = list(Path("input/bidsignore").glob("*"))
            if len(bidsignore_list) > 0:
                bidsignore_path = str(bidsignore_list[0])
                if bidsignore_path:
                    shutil.copy(bidsignore_path, "work/bids/.bidsignore")
                    log.info("Installed .bidsignore in work/bids/")

            try:
                if do_validate_bids:
                    # validate (assume returns 1.. something <10 on error)
                    err_code = validate_bids(bids_path)
                else:
                    log.info("Not running BIDS validation")
                    err_code = 0

            except Exception as exc:
                log.exception(exc, exc_info=True)
                extra_tree_text += f"EXCEPTION: {exc}\n"
                err_code = 22

        else:  # Nothing was downloaded, so what's the point?
            msg = "No BIDS data was found to download"
            log.critical(msg)
            extra_tree_text += f"{msg}\n"
            err_code = 26  # no BIDS data was downloaded

    else:
        # try the usual path in case it was partially created
        bids_path = Path("work/bids")
        extra_tree_text += f"Warning: no bids path, checked work/bids anyway.\n"

    if err_code > 0:
        msg = "Error in BIDS download or validation.  See log for details."
        log.error(msg)
        extra_tree_text += f"{msg}\n"
        # do not bother processing BIDS data

    else:
        msg = "Downloading BIDS data was successful!"
        log.info(msg)
        extra_tree_text += msg

    if tree:
        tree_bids(
            bids_path,
            str(Path(gtk_context.output_dir) / "bids_tree"),
            tree_title,
            extra_tree_text,
        )

    return err_code
