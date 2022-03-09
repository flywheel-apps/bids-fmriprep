import json
import logging
import pprint
from pathlib import Path
from unittest import TestCase

import flywheel_gear_toolkit
import toml

import run

FWV0 = Path.cwd()


def test_fake_data_killed(
    caplog, capfd, install_gear, search_caplog, print_captured,
):

    caplog.set_level(logging.DEBUG)

    user_json = Path(Path.home() / ".config/flywheel/user.json")
    if not user_json.exists():
        TestCase.skipTest("", f"No API key available in {str(user_json)}")
    with open(user_json) as json_file:
        data = json.load(json_file)
        if "ga" not in data["key"]:
            TestCase.skipTest("", "Not logged in to ga.")

    install_gear("fake_data.zip")

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:

        Path("/home/fmriprep/.cache/templateflow/").chmod(0o555)

        status = run.main(gtk_context)

        assert Path(
            "/flywheel/v0/templateflow/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-02_label-WM_probseg.nii.gz"
        ).is_file()

        assert (
            Path(
                "/flywheel/v0/templateflow/tpl-OASIS30ANTs/tpl-OASIS30ANTs_res-01_label-WM_probseg.nii.gz"
            )
            .stat()
            .st_size
            != 0
        )

        toml_file = list(FWV0.glob("work/*/config.toml"))[0]
        assert toml_file.exists()
        toml_info = toml.load(toml_file)
        pprint.pprint(toml_info, indent=2)

        captured = capfd.readouterr()
        print_captured(captured)

        assert status == 1

        assert "freesurfer/license.txt" in toml_info["execution"]["fs_license_file"]

        # assert toml_info["execution"]["templateflow_home"] == str(FWV0 / "templateflow")
        assert search_caplog(caplog, "Unable to execute command")
        assert search_caplog(
            caplog, "Sadly, fMRIPrep did not work on the first or second try"
        )
