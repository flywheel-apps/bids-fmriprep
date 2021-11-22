import logging
from pathlib import Path
from unittest import TestCase

import flywheel_gear_toolkit

import run


def test_wet_run_errors(
    caplog, capfd, install_gear, search_caplog, print_captured, search_caplog_contains,
):

    caplog.set_level(logging.DEBUG)

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")

    # This fake gear must have a destination that has an analysis on a session that has
    # no bold scans (like BIDS_multi_session/ses-Session2).  It downloads the BIDS data
    # for that session and the lack of a bold scan will cause the expected error.
    install_gear("wet_run.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        status = run.main(gtk_context)

        captured = capfd.readouterr()
        print_captured(captured)

        assert status == 1
        assert search_caplog(caplog, "sub-TOME3024_ses-Session2_acq-MPRHA_T1w.nii.gz")
        assert search_caplog(caplog, "Not running BIDS validation")
        assert search_caplog(caplog, "Unable to execute command")
        assert search_caplog(caplog, "RuntimeError: No BOLD images found")
        # Make sure "=" is not after "--ignore"
        assert search_caplog_contains(
            caplog, "command is:", "--ignore fieldmaps slicetiming"
        )
