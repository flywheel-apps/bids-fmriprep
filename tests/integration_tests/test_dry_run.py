import logging
from pathlib import Path
from unittest import TestCase

import flywheel_gear_toolkit

import run

log = logging.getLogger(__name__)


def test_dry_run_works(caplog, install_gear, search_caplog_contains, search_caplog):

    caplog.set_level(logging.DEBUG)

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")

    FWV0 = Path.cwd()

    install_gear("dry_run.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        status = run.main(gtk_context)

        assert status == 0
        assert (FWV0 / "work/bids/.bidsignore").exists()
        assert search_caplog_contains(caplog, "command is", "participant")
        assert search_caplog_contains(caplog, "command is", "'arg1', 'arg2'")
        assert search_caplog(caplog, "No BIDS errors detected.")
        assert search_caplog(caplog, "Zipping work directory")
        assert search_caplog(caplog, "Zipping work/bids/dataset_description.json")
        assert search_caplog(caplog, "Zipping work/bids/sub-TOME3024/ses-Session2/anat")
        assert search_caplog(caplog, "Looked for anatsub-TOME3024_desc-about_T1w.html")
        assert search_caplog(caplog, "Warning: gear-dry-run is set")
