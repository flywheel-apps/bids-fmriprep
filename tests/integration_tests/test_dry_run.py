import logging
import os
from pathlib import Path
from unittest import TestCase

import flywheel_gear_toolkit
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

import run

log = logging.getLogger(__name__)


def test_dry_run_works(
    tmp_path, caplog, install_gear, search_caplog_contains, search_caplog
):

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
        assert search_caplog(caplog, "including sub-TOME3024/figures")
        assert search_caplog(caplog, "Zipping work directory")
        assert search_caplog(caplog, "Zipping work/bids/dataset_description.json")
        assert search_caplog(caplog, "Zipping work/bids/sub-TOME3024/ses-Session2/anat")
        assert search_caplog(caplog, "Looked for anatsub-TOME3024_desc-about_T1w.html")
        assert search_caplog(caplog, "Warning: gear-dry-run is set")

        # Make sure platform-viewable archive includes figures
        html_zip_file = FWV0 / "output/sub-TOME3024_5ebbfe82bfda51026d6aa079.html.zip"
        assert html_zip_file.exists()
        unzip_archive(html_zip_file, tmp_path)
        assert Path(tmp_path / "index.html").exists()
        assert Path(
            tmp_path
            / "sub-TOME3024/figures/sub-TOME3024_ses-Session2_acq-MPRHA_dseg.svg"
        ).exists()
