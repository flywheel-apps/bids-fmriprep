import json
import logging
import os
import shutil
from pathlib import Path
from pprint import pprint
from unittest import TestCase

import flywheel_gear_toolkit
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

import run

WORK = (
    "/flywheel/v0/output/bids-fmriprep_work_ses-Session2_5ebbfe82bfda51026d6aa079.zip"
)
RESULT = "/flywheel/v0/output/bids-fmriprep_ses-Session2_5ebbfe82bfda51026d6aa079.zip"


def test_dry_run_works(
    capfd,
    install_gear,
    print_captured,
    search_stdout_contains,
    search_sysout,
    search_syserr,
):

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")

    install_gear("dry_run.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        status = run.main(gtk_context)

        captured = capfd.readouterr()
        print_captured(captured)

        assert status == 0
        assert Path("/flywheel/v0/work/bids/.bidsignore").exists()
        assert search_stdout_contains(captured, "command is", "participant")
        assert search_stdout_contains(captured, "command is", "'arg1', 'arg2'")
        assert search_syserr(captured, "No BIDS errors detected.")
        assert search_sysout(captured, "Zipping work directory")
        assert search_sysout(captured, "Zipping work/bids/dataset_description.json")
        assert search_sysout(
            captured, "Zipping work/reportlets/somecmd/sub-TOME3024/anat"
        )
        assert search_sysout(captured, "Warning: gear-dry-run is set")

        # Warning occured for missing file expected in intermediate output
        assert search_stdout_contains(
            captured, "WARNING", "Looked for anatsub-TOME3024_desc-about_T1w.html"
        )

        # gear-save-intermediate-output saved work dir
        assert Path(WORK).exists()

        # html report was generated for viewing on platform
        assert Path(
            "/flywheel/v0/output/sub-TOME3024_5ebbfe82bfda51026d6aa079.html.zip"
        ).exists()

        # Make sure results are as expected
        unzip_archive(RESULT, "/tmp")
        assert Path("/tmp/5ebbfe82bfda51026d6aa079/freesurfer").exists()
        # fsaverage was deleted
        assert not Path("/tmp/5ebbfe82bfda51026d6aa079/freesurfer/fsaverage").exists()
        assert Path(
            "/tmp/5ebbfe82bfda51026d6aa079/freesurfer/sub-TOME3024/stats/aseg.stats"
        ).exists()
