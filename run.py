#!/usr/bin/env python3
"""Run the gear: set up for and call command-line command."""

import logging
import os
import re
import shutil
import sys
from pathlib import Path

import flywheel_gear_toolkit
from flywheel_gear_toolkit.interfaces.command_line import (
    build_command_list,
    exec_command,
)
from flywheel_gear_toolkit.utils.zip_tools import zip_output

from utils.bids.download_run_level import download_bids_for_runlevel
from utils.bids.run_level import get_analysis_run_level_and_hierarchy
from utils.dry_run import pretend_it_ran
from utils.fly.environment import get_and_log_environment
from utils.fly.make_file_name_safe import make_file_name_safe
from utils.fly.set_performance_config import set_mem_gb, set_n_cpus
from utils.freesurfer import install_freesurfer_license
from utils.results.zip_htmls import zip_htmls
from utils.results.zip_intermediate import (
    zip_all_intermediate_output,
    zip_intermediate_selected,
)
from utils.singularity import run_in_tmp_dir

log = logging.getLogger(__name__)

GEAR = "bids-fmriprep"
REPO = "flywheel-apps"
CONTAINER = f"{REPO}/{GEAR}]"

BIDS_APP = "fmriprep"

# What level to run at (positional_argument #3)
ANALYSIS_LEVEL = "participant"

# when downloading BIDS Limit download to specific folders
DOWNLOAD_MODALITIES = ["anat", "func", "fmap"]  # empty list is no limit

# Whether or not to include src data (e.g. dicoms) when downloading BIDS
DOWNLOAD_SOURCE = False

# Constants that do not need to be changed
FREESURFER_LICENSE = "./freesurfer/license.txt"


def generate_command(config, work_dir, output_analysis_id_dir, errors, warnings):
    """Build the main command line command to run.

    Args:
        config (GearToolkitContext.config): run-time options from config.json
        work_dir (path): scratch directory where non-saved files can be put
        output_analysis_id_dir (path): directory where output will be saved
        errors (list of str): error messages
        warnings (list of str): warning messages

    Returns:
        cmd (list of str): command to execute
    """

    # start with the command itself:
    cmd = [
        BIDS_APP,
        str(work_dir / "bids"),
        str(output_analysis_id_dir),
        ANALYSIS_LEVEL,
    ]

    # 3 positional args: bids path, output dir, 'participant'
    # This should be done here in case there are nargs='*' arguments
    # These follow the BIDS Apps definition (https://github.com/BIDS-Apps)

    # get parameters to pass to the command by skipping gear config parameters
    # (which start with "gear-") and singularity commands.
    skip_pattern = re.compile("gear-|lsf-|singularity-")

    command_parameters = {}
    for key, val in config.items():

        # these arguments are passed directly to the command as is
        if key == "bids_app_args":
            bids_app_args = val.split(" ")
            for baa in bids_app_args:
                cmd.append(baa)

        elif not skip_pattern.match(key):
            command_parameters[key] = val

    # Validate the command parameter dictionary - make sure everything is
    # ready to run so errors will appear before launching the actual gear
    # code.  Add descriptions of problems to errors & warnings lists.
    # print("command_parameters:", json.dumps(command_parameters, indent=4))

    cmd = build_command_list(cmd, command_parameters)

    for ii, cc in enumerate(cmd):
        if cc.startswith("--verbose"):
            # handle a 'count' argparse argument where manifest gives
            # enumerated possibilities like v, vv, or vvv
            # e.g. replace "--verbose=vvv' with '-vvv'
            cmd[ii] = "-" + cc.split("=")[1]
        elif " " in cc:  # then is is a space-separated list so take out "="
            # this allows argparse "nargs" to work properly
            cmd[ii] = cc.replace("=", " ")

    log.info("command is: %s", str(cmd))
    return cmd


def main(gtk_context):

    FWV0 = Path.cwd()
    log.debug("Running gear in %s", FWV0)

    gtk_context.log_config()

    # Errors and warnings will be always logged when they are detected.
    # Keep a list of errors and warning to print all in one place at end of log
    # Any errors will prevent the command from running and will cause exit(1)
    errors = []
    warnings = []

    output_dir = gtk_context.output_dir
    log.debug("output_dir is %s", output_dir)
    work_dir = gtk_context.work_dir
    log.debug("work_dir is %s", work_dir)
    gear_name = gtk_context.manifest["name"]

    # run-time configuration options from the gear's context.json
    config = gtk_context.config

    dry_run = config.get("gear-dry-run")

    # Given the destination container, figure out if running at the project,
    # subject, or session level.
    destination_id = gtk_context.destination["id"]
    hierarchy = get_analysis_run_level_and_hierarchy(gtk_context.client, destination_id)

    # This is the label of the project, subject or session and is used
    # as part of the name of the output files.
    run_label = make_file_name_safe(hierarchy["run_label"])

    # Output will be put into a directory named as the destination id.
    # This allows the raw output to be deleted so that a zipped archive
    # can be returned.
    output_analysis_id_dir = output_dir / destination_id

    environ = get_and_log_environment()

    # set # threads and max memory to use
    config["n_cpus"], config["omp-nthreads"] = set_n_cpus(
        config.get("n_cpus"), config.get("omp-nthreads")
    )
    config["mem"] = set_mem_gb(config.get("mem"))

    environ["OMP_NUM_THREADS"] = str(config["omp-nthreads"])

    # All writeable directories need to be set up in the current working directory

    orig_subject_dir = Path(environ["SUBJECTS_DIR"])
    subjects_dir = FWV0 / "freesurfer/subjects"
    environ["SUBJECTS_DIR"] = str(subjects_dir)
    if not subjects_dir.exists():  # needs to be created unless testing
        subjects_dir.mkdir(parents=True)
        (subjects_dir / "fsaverage").symlink_to(orig_subject_dir / "fsaverage")
        (subjects_dir / "fsaverage5").symlink_to(orig_subject_dir / "fsaverage5")
        (subjects_dir / "fsaverage6").symlink_to(orig_subject_dir / "fsaverage6")

    environ["FS_LICENSE"] = str(FWV0 / "freesurfer/license.txt")

    license_list = list(Path("input/freesurfer_license").glob("*"))
    if len(license_list) > 0:
        fs_license_path = license_list[0]
    else:
        fs_license_path = ""
    install_freesurfer_license(
        str(fs_license_path),
        config.get("gear-FREESURFER_LICENSE"),
        gtk_context.client,
        destination_id,
        FREESURFER_LICENSE,
    )

    templateflow_dir = FWV0 / "templateflow"
    templateflow_dir.mkdir()
    environ["SINGULARITYENV_TEMPLATEFLOW_HOME"] = str(templateflow_dir)
    environ["TEMPLATEFLOW_HOME"] = str(templateflow_dir)

    command = generate_command(
        config, work_dir, output_analysis_id_dir, errors, warnings
    )

    # This is used as part of the name of output files
    command_name = make_file_name_safe(command[0])

    # Download BIDS Formatted data
    if len(errors) == 0:

        # Create HTML file that shows BIDS "Tree" like output
        tree = True
        tree_title = f"{command_name} BIDS Tree"

        error_code = download_bids_for_runlevel(
            gtk_context,
            hierarchy,
            tree=tree,
            tree_title=tree_title,
            src_data=DOWNLOAD_SOURCE,
            folders=DOWNLOAD_MODALITIES,
            dry_run=dry_run,
            do_validate_bids=config.get("gear-run-bids-validation"),
        )
        if error_code > 0 and not config.get("gear-ignore-bids-errors"):
            errors.append(f"BIDS Error(s) detected.  Did not run {CONTAINER}")

    else:
        log.info("Did not download BIDS because of previous errors")
        print(errors)

    # Don't run if there were errors or if this is a dry run
    return_code = 0

    try:

        if len(errors) > 0:
            return_code = 1
            log.info("Command was NOT run because of previous errors.")

        elif dry_run:
            e = "gear-dry-run is set: Command was NOT run."
            log.warning(e)
            warnings.append(e)
            pretend_it_ran(destination_id)

        else:
            # Create output directory
            log.info("Creating output directory %s", output_analysis_id_dir)
            Path(output_analysis_id_dir).mkdir()

            if config["gear-log-level"] != "INFO":
                # show what's in the current working directory just before running
                os.system("tree -a .")

            if "gear-timeout" in config:
                command = [f"timeout {config['gear-timeout']}"] + command

            # This is what it is all about
            exec_command(
                command, environ=environ, dry_run=dry_run, shell=True, cont_output=True,
            )

    except RuntimeError as exc:
        return_code = 1
        errors.append(exc)
        log.critical(exc)
        log.exception("Unable to execute command.")

    finally:

        # Cleanup, move all results to the output directory

        # Remove all fsaverage* directories
        if not config.get("gear-keep-fsaverage"):
            path = output_analysis_id_dir / "freesurfer"
            fsavg_dirs = path.glob("fsaverage*")
            for fsavg in fsavg_dirs:
                log.info("deleting %s", str(fsavg))
                shutil.rmtree(fsavg)
        else:
            log.info("Keeping fsaverage directories")

        # zip entire output/<analysis_id> folder into
        #  <gear_name>_<project|subject|session label>_<analysis.id>.zip
        zip_file_name = gear_name + f"_{run_label}_{destination_id}.zip"
        zip_output(
            str(output_dir),
            destination_id,
            zip_file_name,
            dry_run=False,
            exclude_files=None,
        )

        # Make archives for result *.html files for easy display on platform
        zip_htmls(output_dir, destination_id, output_analysis_id_dir / BIDS_APP)

        # possibly save ALL intermediate output
        if config.get("gear-save-intermediate-output"):
            zip_all_intermediate_output(
                destination_id, gear_name, output_dir, work_dir, run_label
            )

        # possibly save intermediate files and folders
        zip_intermediate_selected(
            config.get("gear-intermediate-files"),
            config.get("gear-intermediate-folders"),
            destination_id,
            gear_name,
            output_dir,
            work_dir,
            run_label,
        )

        # clean up: remove output that was zipped
        if Path(output_analysis_id_dir).exists():
            if not config.get("gear-keep-output"):

                log.debug('removing output directory "%s"', str(output_analysis_id_dir))
                shutil.rmtree(output_analysis_id_dir)

            else:
                log.info(
                    'NOT removing output directory "%s"', str(output_analysis_id_dir)
                )

        else:
            log.info("Output directory does not exist so it cannot be removed")

        # Report errors and warnings at the end of the log so they can be easily seen.
        if len(warnings) > 0:
            msg = "Previous warnings:\n"
            for warn in warnings:
                msg += "  Warning: " + str(warn) + "\n"
            log.info(msg)

        if len(errors) > 0:
            msg = "Previous errors:\n"
            for err in errors:
                if str(type(err)).split("'")[1] == "str":
                    # show string
                    msg += "  Error msg: " + str(err) + "\n"
                else:  # show type (of error) and error message
                    err_type = str(type(err)).split("'")[1]
                    msg += f"  {err_type}: {str(err)}\n"
            log.info(msg)
            return_code = 1

    log.info("%s Gear is done.  Returning %s", CONTAINER, return_code)

    return return_code


if __name__ == "__main__":

    # always run in a newly created "scratch" directory in /tmp/...
    scratch_dir = run_in_tmp_dir()

    gtk_context = flywheel_gear_toolkit.GearToolkitContext()

    # Setup basic logging and log the configuration for this job
    if gtk_context.config["gear-log-level"] == "INFO":
        gtk_context.init_logging("info")
    else:
        gtk_context.init_logging("debug")

    return_code = main(gtk_context)

    # clean up (might be necessary when running in a shared computing environment)
    for thing in scratch_dir.glob("*"):
        if thing.is_symlink():
            thing.unlink()  # don't remove anything links point to
            log.debug("unlinked %s", thing.name)
    shutil.rmtree(scratch_dir)
    log.debug("Removed %s", scratch_dir)

    sys.exit(return_code)
