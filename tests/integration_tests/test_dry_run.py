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
        assert (FWV0 / "freesurfer/subjects/sub-42/label/empty").exists()
        assert search_caplog_contains(
            caplog,
            "command is",
            "--bids-filter-file=input/bids-filter-file/PyBIDS_filter.json",
        )
        assert search_caplog_contains(
            caplog, "--work-dir", "flywheel/v0/output/61608fc7dbf5f9487f231006"
        )

        # Since the "work-dir" option was used, the gear created the old data's /tmp/ path and
        # ran in it, and a symbolic link was created from the current /tmp/ path to the old one.
        # The "current" path was created just before these tests started (in conftest.py). E.g.:
        # % ls /tmp
        # gear-temp-dir-2cde80oy -> /tmp/gear-temp-dir-yhv7hq29
        # gear-temp-dir-yhv7hq29
        # where "yhv7hq29" is the old random part found in the provided "work-dir" data and
        # "2cde80oy" is the new random part of the /tmp/ path created to run these tests.
        # The new part is generated randomly so it will change but the old one is in the gear test
        # data provided as an input to the gear.
        old_tmp_path = Path(*(list(Path.cwd().parts)[:3]))
        assert "yhv7hq29" in list(old_tmp_path.parts)[2]
        current_tmp_path = Path(*(list(FWV0.parts)[:3]))
        assert current_tmp_path.is_symlink()
        # now change back to the original /tmp/ path so that following tests will not be affected
        current_tmp_path.unlink()
        old_tmp_path.replace(current_tmp_path)

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
        html_zip_files = list(FWV0.glob("output/sub-TOME3024_*.html.zip"))
        html_zip_file = html_zip_files[0]
        assert html_zip_file.exists()
        unzip_archive(html_zip_file, tmp_path)
        assert Path(tmp_path / "index.html").exists()
        assert Path(
            tmp_path
            / "sub-TOME3024/figures/sub-TOME3024_ses-Session2_acq-MPRHA_dseg.svg"
        ).exists()
