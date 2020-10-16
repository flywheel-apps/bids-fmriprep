import json
import os
import shutil
from pathlib import Path

import pytest
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

FS_DIR = Path("/usr/local/freesurfer/")
SUBJECTS_DIR = Path(FS_DIR / "subjects")


@pytest.fixture
def install_gear():
    def _method(zip_name):
        """unarchive initial gear to simulate running inside a real gear.

        This will delete and then install: config.json input/ output/ work/

        Args:
            zip_name (str): name of zip file that holds simulated gear.
        """

        gear_tests = "/src/tests/data/gear_tests/"
        gear = "/flywheel/v0/"
        os.chdir(gear)  # Make sure we're in the right place (gear works in "work/" dir)

        print("\nRemoving previous gear...")

        if Path(gear + "config.json").exists():
            Path(gear + "config.json").unlink()

        for dir_name in ["input", "output", "work", "freesurfer"]:
            path = Path(gear + dir_name)
            if path.exists():
                shutil.rmtree(path)

        print(f'\ninstalling new gear, "{zip_name}"...')
        unzip_archive(gear_tests + zip_name, gear)

        # move freesurfer license and subject directories to proper place
        gear_freesurfer = Path("freesurfer")
        if gear_freesurfer.exists():
            if not SUBJECTS_DIR.exists():
                print(f"WARNING: had to create {SUBJECTS_DIR}")
                SUBJECTS_DIR.mkdir(parents=True)
            gear_license = Path(gear_freesurfer / "license.txt")
            if gear_license.exists():
                if Path(FS_DIR / "license.txt").exists():
                    Path(FS_DIR / "license.txt").unlink()
                shutil.move(str(gear_license), str(FS_DIR))
            subjects = gear_freesurfer.glob("subjects/*")
            for subj in subjects:
                subj_name = subj.name
                if (SUBJECTS_DIR / subj_name).exists():
                    shutil.rmtree(SUBJECTS_DIR / subj_name)
                print(f"moving subject to {str(SUBJECTS_DIR / subj_name)}")
                shutil.move(str(subj), str(SUBJECTS_DIR))

    return _method


@pytest.fixture
def print_captured():
    def _method(captured):
        """Show what has been captured in std out and err."""

        print("\nout")
        for ii, msg in enumerate(captured.out.split("\n")):
            print(f"{ii:2d} {msg}")
        print("\nerr")
        for ii, msg in enumerate(captured.err.split("\n")):
            print(f"{ii:2d} {msg}")

    return _method


@pytest.fixture
def search_stdout_contains():
    def _method(captured, find_me, contains_me):
        """Search stdout message for find_me, return true if it contains contains_me"""

        for msg in captured.out.split("/n"):
            if find_me in msg:
                print(f"Found '{find_me}' in '{msg}'")
                if contains_me in msg:
                    print(f"Found '{contains_me}' in '{msg}'")
                    return True
        return False

    return _method


@pytest.fixture
def search_sysout():
    def _method(captured, find_me):
        """Search capsys message for find_me, return message"""

        for msg in captured.out.split("/n"):
            if find_me in msg:
                return msg
        return ""

    return _method


@pytest.fixture
def search_syserr():
    def _method(captured, find_me):
        """Search capsys message for find_me, return message"""

        for msg in captured.err.split("\n"):
            if find_me in msg:
                return msg
        return ""

    return _method


@pytest.fixture
def print_caplog():
    def _method(caplog):
        """Show what has been captured in the log."""

        print("\nmessages")
        for ii, msg in enumerate(caplog.messages):
            print(f"{ii:2d} {msg}")
        print("\nrecords")
        for ii, rec in enumerate(caplog.records):
            print(f"{ii:2d} {rec}")

    return _method


@pytest.fixture
def search_caplog():
    def _method(caplog, find_me):
        """Search caplog message for find_me, return message"""

        for msg in caplog.messages:
            if find_me in msg:
                return msg
        return ""

    return _method


@pytest.fixture
def search_caplog_contains():
    def _method(caplog, find_me, contains_me):
        """Search caplog message for find_me, return true if it contains contains_me"""

        for msg in caplog.messages:
            if find_me in msg:
                print(f"Found '{find_me}' in '{msg}'")
                if contains_me in msg:
                    print(f"Found '{contains_me}' in '{msg}'")
                    return True
        return False

    return _method
