import logging
from pathlib import Path
from unittest import TestCase

import flywheel_gear_toolkit

import run


def test_bids_error_reports(caplog, install_gear, search_caplog):

    caplog.set_level(logging.DEBUG)

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")

    install_gear("bids_error.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        status = run.main(gtk_context)

        assert status == 1
        assert search_caplog(caplog, "bids-validator return code: 1")
        assert search_caplog(caplog, "3 BIDS validation error(s) were detected")
        assert search_caplog(caplog, "anat/sub-TOME3024_ses-Session2_acq-MPR_T1w.jsen")
