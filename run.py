#!/usr/bin/env python3
"""Run the gear: set up for and call command-line command."""

import json
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
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive, zip_output

from utils.bids.download_run_level import download_bids_for_runlevel
from utils.bids.run_level import get_analysis_run_level_and_hierarchy
from utils.dry_run import pretend_it_ran
from utils.fly.environment import get_and_log_environment
from utils.fly.make_file_name_safe import make_file_name_safe
from utils.fly.set_performance_config import set_mem_mb, set_n_cpus
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
CONTAINER = Path(REPO).joinpath(GEAR)

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
        "/usr/bin/time",
        "-v",
        "--output=time_output.txt",
        BIDS_APP,
        os.path.join(work_dir, "bids"),
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
    log.info("Running gear in %s", FWV0)

    gtk_context.log_config()

    # Errors and warnings will be always logged when they are detected.
    # Keep a list of errors and warning to print all in one place at end of log
    # Any errors will prevent the command from running and will cause exit(1)
    errors = []
    warnings = []

    output_dir = gtk_context.output_dir
    log.info("output_dir is %s", output_dir)
    work_dir = gtk_context.work_dir
    log.info("work_dir is %s", work_dir)
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
    log.info("Creating output directory %s", output_analysis_id_dir)
    if Path(output_analysis_id_dir).exists():
        log.info(
            "Not actually creating output directory %s because it exists.  This must be a test",
            output_analysis_id_dir,
        )
    else:
        Path(output_analysis_id_dir).mkdir()

    environ = get_and_log_environment()

    # set # threads and max memory to use
    config["n_cpus"], config["omp-nthreads"] = set_n_cpus(
        config.get("n_cpus"), config.get("omp-nthreads")
    )
    config["mem"] = set_mem_mb(config.get("mem_mb"))

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

    bids_filter_file_path = gtk_context.get_input_path("bids-filter-file")
    if bids_filter_file_path:
        paths = list(Path("input/bids-filter-file").glob("*"))
        log.info("Using provided PyBIDS filter file %s", str(paths[0]))
        config["bids-filter-file"] = str(paths[0])

    subject_zip_file_path = gtk_context.get_input_path("fs-subjects-dir")
    if subject_zip_file_path:
        paths = list(Path("input/fs-subjects-dir").glob("*"))
        log.info("Using provided Freesurfer subject file %s", str(paths[0]))
        unzip_dir = FWV0 / "unzip-fs-subjects-dir"
        unzip_dir.mkdir(parents=True)
        unzip_archive(paths[0], unzip_dir)
        for a_subject in unzip_dir.glob("*/*"):
            if (subjects_dir / a_subject.name).exists():
                log.info("Found %s but using existing", a_subject.name)
            else:
                log.info("Found %s", a_subject.name)
                a_subject.rename(subjects_dir / a_subject.name)
        config["fs-subjects-dir"] = subjects_dir

    previous_results_zip_file_path = gtk_context.get_input_path("previous-results")
    if previous_results_zip_file_path:
        paths = list(Path("input/previous-results").glob("*"))
        log.info("Using provided fMRIPrep previous results file %s", str(paths[0]))
        unzip_dir = FWV0 / "unzip-previous-results"
        unzip_dir.mkdir(parents=True)
        unzip_archive(paths[0], unzip_dir)
        for a_dir in unzip_dir.glob("*/*"):
            log.info("Found %s", a_dir.name)
            a_dir.rename(output_analysis_id_dir / a_dir.name)

    config_file = gtk_context.get_input_path("config-file")
    if config_file:
        config['config-file'] = config_file


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

    # TemplateFlow seems to be baked in to the container since 2021-10-07 16:25:12 so this is not needed...actually, it is for now...
    templateflow_dir = FWV0 / "templateflow"
    templateflow_dir.mkdir()
    environ["SINGULARITYENV_TEMPLATEFLOW_HOME"] = str(templateflow_dir)
    environ["TEMPLATEFLOW_HOME"] = str(templateflow_dir)
    orig = Path("/home/fmriprep/.cache/templateflow/")
    # Fill writable templateflow directory with existing templates so they don't have to be downloaded
    templates = list(orig.glob("*"))
    for tt in templates:
        # (templateflow_dir / tt.name).symlink_to(tt)
        shutil.copytree(tt, templateflow_dir / tt.name)

    command = generate_command(
        config, work_dir, output_analysis_id_dir, errors, warnings
    )

    # Download BIDS Formatted data
    if len(errors) == 0:

        # Create HTML file that shows BIDS "Tree" like output
        tree = True
        tree_title = f"{gear_name} BIDS Tree"

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

    return_code = 0
    num_tries = 0

    # Don't run if there were errors or if this is a dry run
    if len(errors) > 0:
        return_code = 1
        log.info("Command was NOT run because of previous errors.")
        num_tries == 2  # don't try to run

    while num_tries < 2:

        try:

            num_tries += 1
            if num_tries > 1:
                log.info("Trying a second time")

            if dry_run:
                e = "gear-dry-run is set: Command was NOT run."
                log.warning(e)
                warnings.append(e)
                pretend_it_ran(destination_id)

            else:

                if "gear-timeout" in config:
                    command = [f"timeout {config['gear-timeout']}"] + command

                if config["gear-log-level"] != "INFO":
                    # show what's in the current working directory just before running
                    os.system("tree -alh .")

                # This is what it is all about
                exec_command(
                    command,
                    environ=environ,
                    dry_run=dry_run,
                    shell=True,
                    cont_output=True,
                )

        except RuntimeError as exc:
            return_code = 1
            errors.append(exc)
            log.critical(exc)
            log.exception("Unable to execute command.")

    # Save time, etc. resources used in metadata on analysis
    if Path("time_output.txt").exists():  # some tests won't have this file
        metadata = {
            "analysis": {"info": {"resources used": {},},},
        }
        with open("time_output.txt") as file:
            for line in file:
                if ":" in line:
                    if (
                        "Elapsed" in line
                    ):  # special case "Elapsed (wall clock) time (h:mm:ss or m:ss): 0:08.11"
                        sline = re.split(r"\):", line)
                        sline[0] += ")"
                    else:
                        sline = line.split(":")
                    key = sline[0].strip()
                    val = sline[1].strip(' "\n')
                    metadata["analysis"]["info"]["resources used"][key] = val
        with open(f"{output_dir}/.metadata.json", "w") as fff:
            json.dump(metadata, fff)
            log.info(f"Wrote {output_dir}/.metadata.json")

    # Cleanup, move all results to the output directory

    if return_code != 0:
        os.system("echo ")
        os.system("echo Disk Information on Failure")
        os.system("df -h")

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
            log.info('NOT removing output directory "%s"', str(output_analysis_id_dir))

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

    if num_tries == 1:
        log.info("Happily, fMRIPrep worked on the first try.")
    else:
        msg = (
            "first try but it did on the second"
            if return_code == 0
            else "first or second try"
        )
        log.info("Sadly, fMRIPrep did not work on the %s.", msg)

    log.info("%s Gear is done.  Returning %s", CONTAINER, return_code)

    return return_code


if __name__ == "__main__":

    with flywheel_gear_toolkit.GearToolkitContext() as gtk_context:

        # make sure /flywheel/v0 is writable, use a scratch directory if not
        scratch_dir = run_in_tmp_dir(gtk_context.config["gear-writable-dir"])

        return_code = main(gtk_context)

        # clean up (might be necessary when running in a shared computing environment)
        if scratch_dir:
            log.debug("Removing scratch directory")
            for thing in scratch_dir.glob("*"):
                if thing.is_symlink():
                    thing.unlink()  # don't remove anything links point to
                    log.debug("unlinked %s", thing.name)
            shutil.rmtree(scratch_dir)
            log.debug("Removed %s", scratch_dir)

    sys.exit(return_code)
