#!/usr/bin/env python3
"""Run the gear: set up for and call command-line command."""

import json
import os
import shutil
import sys
from pathlib import Path

import flywheel_gear_toolkit
import psutil
from flywheel_gear_toolkit.interfaces.command_line import (
    build_command_list,
    exec_command,
)
from flywheel_gear_toolkit.licenses.freesurfer import install_freesurfer_license
from flywheel_gear_toolkit.utils.zip_tools import zip_output

from utils.bids.download_run_level import download_bids_for_runlevel
from utils.bids.run_level import get_run_level_and_hierarchy
from utils.dry_run import pretend_it_ran
from utils.fly.make_file_name_safe import make_file_name_safe
from utils.results.zip_htmls import zip_htmls
from utils.results.zip_intermediate import (
    zip_all_intermediate_output,
    zip_intermediate_selected,
)

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
FREESURFER_LICENSE = "/opt/freesurfer/license.txt"
ENVIRONMENT_FILE = "/tmp/gear_environ.json"


def set_performance_config(config, log):
    """Set run-time performance config params to pass to BIDS App.

    Set --n_cpus (number of threads) and --mem_mb (maximum memory to use).
    Use the given number unless it is too big.  Use the max available if zero.

    The user may want to set these number to less than the maximum if using a
    shared compute resource.

    Args:
        config (GearToolkitContext.config): run-time options from config.json
        log (GearToolkitContext().log): logger set up by Gear Toolkit

    Results:
        sets config["n_cpus"] which will become part of the command line command
        sets config["mem_mb"] which will become part of the command line command
    """

    os_cpu_count = os.cpu_count()
    log.info("os.cpu_count() = %d", os_cpu_count)
    n_cpus = config.get("n_cpus")
    if n_cpus:
        if n_cpus > os_cpu_count:
            log.warning("n_cpus > number available, using max %d", os_cpu_count)
            config["n_cpus"] = os_cpu_count
        else:
            log.info("n_cpus using %d from config", n_cpus)
    else:  # Default is to use all cpus available
        config["n_cpus"] = os_cpu_count  # zoom zoom
        log.info("using n_cpus = %d (maximum available)", os_cpu_count)

    psutil_mem_mb = int(psutil.virtual_memory().available / (1024 ** 2))
    log.info("psutil.virtual_memory().available= {:8.2f} MiB".format(psutil_mem_mb))
    mem_mb = config.get("mem_mb")
    if mem_mb:
        if mem_mb > psutil_mem_mb:
            log.warning("mem_mb > number available, using max %d", psutil_mem_mb)
            config["mem_mb"] = psutil_mem_mb
        else:
            log.info("mem_mb using %d from config", n_cpus)
    else:  # Default is to use all cpus available
        config["mem_mb"] = psutil_mem_mb
        log.info("using mem_mb = %d (maximum available)", psutil_mem_mb)


def get_and_log_environment(log):
    """Grab and log environment for to use when executing command line.

    The shell environment is saved into a file at an appropriate place in the Dockerfile.

    Args:
        log (GearToolkitContext().log): logger set up by Gear Toolkit

    Returns: (nothing)
    """
    with open(ENVIRONMENT_FILE, "r") as f:
        environ = json.load(f)

        # Add environment to log if debugging
        kv = ""
        for k, v in environ.items():
            kv += k + "=" + v + " "
        log.debug("Environment: " + kv)

    return environ


def generate_command(config, work_dir, output_analysis_id_dir, log, errors, warnings):
    """Build the main command line command to run.

    Args:
        config (GearToolkitContext.config): run-time options from config.json
        work_dir (path): scratch directory where non-saved files can be put
        output_analysis_id_dir (path): directory where output will be saved
        log (GearToolkitContext().log): logger set up by Gear Toolkit
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
    # (which start with "gear-").
    command_parameters = {}
    for key, val in config.items():

        # these arguments are passed directly to the command as is
        if key == "bids_app_args":
            bids_app_args = val.split(" ")
            for baa in bids_app_args:
                cmd.append(baa)

        elif not key.startswith("gear-"):
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

    log.info("command is: %s", str(cmd))
    return cmd


def main(gtk_context):

    # Keep a list of errors and warning to print all in one place at end of log
    # Any errors will prevent the command from running and will cause exit(1)
    errors = []
    warnings = []

    # run-time configuration options from the gear's context.json
    config = gtk_context.config

    # Setup basic logging and log the configuration for this job
    if config["gear-log-level"] == "INFO":
        gtk_context.init_logging("info")
    else:
        gtk_context.init_logging("debug")
    gtk_context.log_config()
    log = gtk_context.log

    # Given the destination container, figure out if running at the project,
    # subject, or session level.
    destination_id = gtk_context.destination["id"]
    hierarchy = get_run_level_and_hierarchy(gtk_context.client, destination_id)

    # This is the label of the project, subject or session and is used
    # as part of the name of the output files.
    run_label = make_file_name_safe(hierarchy["run_label"])

    # Output will be put into a directory named as the destination id.
    # This allows the raw output to be deleted so that a zipped archive
    # can be returned.
    output_analysis_id_dir = gtk_context.output_dir / destination_id

    # set # threads and max memory to use
    set_performance_config(config, log)

    environ = get_and_log_environment(log)

    if Path(FREESURFER_LICENSE).exists():
        log.debug("%s exists.", FREESURFER_LICENSE)
    install_freesurfer_license(gtk_context, FREESURFER_LICENSE)

    command = generate_command(
        config, gtk_context.work_dir, output_analysis_id_dir, log, errors, warnings
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
            dry_run=config.get("gear-dry-run"),
            do_validate_bids=config.get("gear-run-bids-validation"),
        )
        if error_code > 0 and not config.get("gear-ignore-bids-errors"):
            errors.append(f"BIDS Error(s) detected.  Did not run {CONTAINER}")

    else:
        log.info("Did not download BIDS because of previous errors")
        print(errors)

    # Don't run if there were errors or if this is a dry run
    ok_to_run = True
    return_code = 0

    if len(errors) > 0:
        ok_to_run = False
        return_code = 1
        log.info("Command was NOT run because of previous errors.")

    elif config.get("gear-dry-run"):
        ok_to_run = False
        return_code = 0
        e = "gear-dry-run is set: Command was NOT run."
        log.warning(e)
        warnings.append(e)
        pretend_it_ran(gtk_context)

    try:

        if ok_to_run:

            # Create output directory
            log.info("Creating output directory %s", output_analysis_id_dir)
            Path(output_analysis_id_dir).mkdir()

            # This is what it is all about
            exec_command(command, environ=environ)

    except RuntimeError as exc:
        return_code = 1
        errors.append(exc)
        log.critical(exc)
        log.exception("Unable to execute command.")

    finally:

        # Cleanup, move all results to the output directory

        # zip entire output/<analysis_id> folder into
        #  <gear_name>_<project|subject|session label>_<analysis.id>.zip
        zip_file_name = (
            gtk_context.manifest["name"] + f"_{run_label}_{destination_id}.zip"
        )
        zip_output(
            str(gtk_context.output_dir),
            destination_id,
            zip_file_name,
            dry_run=False,
            exclude_files=None,
        )

        # zip any .html files in output/<analysis_id>/
        zip_htmls(gtk_context, output_analysis_id_dir)

        # Remove all fsaverage* directories
        if not config.get("gear-keep-fsaverage"):
            path = output_analysis_id_dir / "freesurfer"
            fsavg_dirs = path.glob("fsaverage*")
            for fsavg in fsavg_dirs:
                log.info("deleting %s", str(fsavg))
                shutil.rmtree(fsavg)
        else:
            log.info("Keeping fsaverage directories")

        # possibly save ALL intermediate output
        if config.get("gear-save-intermediate-output"):
            zip_all_intermediate_output(gtk_context, run_label)

        # possibly save intermediate files and folders
        zip_intermediate_selected(gtk_context, run_label)

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

        # save .metadata file
        metadata = {
            "project": {
                "info": {
                    "test": "Hello project",
                    f"{run_label} {destination_id}": "put this here",
                },
                "tags": [run_label, destination_id],
            },
            "subject": {
                "info": {
                    "test": "Hello subject",
                    f"{run_label} {destination_id}": "put this here",
                },
                "tags": [run_label, destination_id],
            },
            "session": {
                "info": {
                    "test": "Hello session",
                    f"{run_label} {destination_id}": "put this here",
                },
                "tags": [run_label, destination_id],
            },
            "analysis": {
                "info": {
                    "test": "Hello analysis",
                    f"{run_label} {destination_id}": "put this here",
                },
                "files": [
                    {
                        "name": "bids_tree.html",
                        "info": {
                            "value1": "foo",
                            "value2": "bar",
                            f"{run_label} {destination_id}": "put this here",
                        },
                        "tags": ["ein", "zwei"],
                    }
                ],
                "tags": [run_label, destination_id],
            },
        }
        # with open(f"{gtk_context.output_dir}/.metadata.json", "w") as fff:
        #    json.dump(metadata, fff)
        #    log.info(f"Wrote {gtk_context.output_dir}/.metadata.json")

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

    sys.exit(main(flywheel_gear_toolkit.GearToolkitContext()))
