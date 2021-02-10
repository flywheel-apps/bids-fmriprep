import shutil
from pathlib import Path

import pytest
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

from utils.singularity import run_in_tmp_dir

run_in_tmp_dir()  # run all tests in /tmp/*/flywheel/v0 where * is random

FWV0 = Path.cwd()


@pytest.fixture
def install_gear():
    def _method(zip_name):
        """unarchive initial gear to simulate running inside a real gear.

        This will delete and then install: config.json input/ output/ work/ freesurfer/

        Args:
            zip_name (str): name of zip file that holds simulated gear.
        """

        gear_tests = Path("/src/tests/data/gear_tests/")
        if not gear_tests.exists():  # fix for running in circleci
            gear_tests = FWV0 / "tests/data/gear_tests/"

        print("\nRemoving previous gear...")

        if Path(FWV0 / "config.json").exists():
            Path(FWV0 / "config.json").unlink()

        for dir_name in ["input", "output", "work", "freesurfer"]:
            path = Path(FWV0 / dir_name)
            if path.exists():
                print(f"shutil.rmtree({str(path)}")
                shutil.rmtree(path)

        print(f'\ninstalling new gear, "{zip_name}"...')
        unzip_archive(gear_tests / zip_name, str(FWV0))

        # The "freesurfer" direcory needs to have the standard freesurfer
        # "subjects" directory and "license.txt" file.

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
