import logging
from pathlib import Path
from unittest import TestCase

import flywheel_gear_toolkit

import run


def test_wet_run_errors(
    caplog,
    capfd,
    install_gear,
    search_caplog,
    print_captured,
    search_syserr,
    search_caplog_contains,
):

    caplog.set_level(logging.DEBUG)

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")

    install_gear("wet_run.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        status = run.main(gtk_context)

        captured = capfd.readouterr()
        print_captured(captured)

        assert status == 1
        assert search_caplog(caplog, "sub-TOME3024_ses-Session2_acq-MPR_T1w.nii.gz")
        assert search_caplog(caplog, "Not running BIDS validation")
        assert search_caplog(caplog, "Unable to execute command")
        assert search_caplog(caplog, "RuntimeError: No BOLD images found")
        # Make sure "=" is not after "--ignore"
        assert search_caplog_contains(
            caplog, "command is:", "--ignore fieldmaps slicetiming"
        )
