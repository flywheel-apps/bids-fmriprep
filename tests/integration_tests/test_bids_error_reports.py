import json
from pathlib import Path
from unittest import TestCase

import flywheel_gear_toolkit
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

import run


def test_bids_error_reports(
    capfd, install_gear, print_captured, search_sysout, search_syserr
):

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")

    install_gear("bids_error.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        status = run.main(gtk_context)

        captured = capfd.readouterr()
        print_captured(captured)

        assert status == 1
        assert search_sysout(captured, "bids-validator return code: 1")
        assert search_syserr(captured, "3 BIDS validation error(s) were detected")
        assert search_syserr(
            captured, "anat/sub-TOME3024_ses-Session2_acq-MPR_T1w.jsen"
        )
