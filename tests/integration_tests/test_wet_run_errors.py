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


def test_wet_run_errors(
    capfd, install_gear, print_captured, search_sysout, search_syserr
):

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")

    install_gear("wet_run.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        status = run.main(gtk_context)

        captured = capfd.readouterr()
        print_captured(captured)

        assert status == 1
        assert search_sysout(captured, "sub-TOME3024_ses-Session2_acq-MPR_T1w.nii.gz")
        assert search_sysout(captured, "Not running BIDS validation")
        assert search_syserr(captured, "Unable to execute command")
        assert search_syserr(captured, "RuntimeError: No BOLD images found")
        # Make sure "=" was removed when parameter is a space separated list"
        assert search_syserr(captured, "--ignore fieldmaps slicetiming")
        assert search_syserr(captured, "--output-spaces MNI152NLin2009cAsym individual")
