import json
import logging
from pathlib import Path
from unittest import TestCase

import flywheel_gear_toolkit
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

import run

log = logging.getLogger(__name__)


def test_fs_subjects_dir_works(
    tmp_path, caplog, install_gear, search_caplog_contains, search_caplog
):

    caplog.set_level(logging.DEBUG)

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")
    with open(user_json) as json_file:
        data = json.load(json_file)
        if "ga" not in data["key"]:
            TestCase.skipTest("", "Not logged in to ga.")

    FWV0 = Path.cwd()

    install_gear("fs-subjects-dir.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        status = run.main(gtk_context)

        assert status == 0
        assert search_caplog(caplog, 'Input file "fs-subjects-dir" is')
        # make sure freesurfer subject made it
        assert (
            FWV0 / "freesurfer/subjects/sub-TOME3024/scripts/recon-all.log"
        ).exists()
        assert search_caplog(caplog, "Warning: gear-dry-run is set")
