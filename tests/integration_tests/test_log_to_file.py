import json
import logging
import os
from pathlib import Path
from unittest import TestCase

import flywheel_gear_toolkit
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

import run

log = logging.getLogger(__name__)


def test_log_to_file_works(
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

    install_gear("log_to_file.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        status = run.main(gtk_context)

        assert status == 1
        log_path = Path("/flywheel/v0/output/log2.txt")
        assert log_path.exists()
        found_it = False
        with open(log_path, "r") as ff:
            for line in ff:
                if "Running fMRIPREP" in line:
                    found_it = True
                    break
        assert found_it
        assert 0
