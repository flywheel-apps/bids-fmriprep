import json
import logging
from pathlib import Path

import pytest
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive

from utils.results.zip_intermediate import zip_intermediate_selected, zip_selected


@pytest.fixture
def create_test_files(tmp_path):
    root_dir = tmp_path
    dir_name = "test"
    source_dir = Path(root_dir) / dir_name
    dirs = ["one", "two", "four", "one/three", "something/else", "dir_not_included"]
    files = [
        "one/hey",
        "two/hee",
        "one/three/now",
        "something/else/altogether",
        "four/hey",
        "four/not_included",
        "dir_not_included/skipped",
    ]
    if Path(source_dir).exists():
        shutil.rmtree(source_dir)
    for dd in dirs:
        Path(source_dir / dd).mkdir(parents=True)
    for ff in files:
        Path(source_dir / ff).touch()
    yield source_dir


def test_zip_selected_works(create_test_files, caplog, print_caplog, search_caplog):

    caplog.set_level(logging.DEBUG)

    work_dir = create_test_files
    work_path = work_dir.parents[0]
    dest_zip = work_path / "destination_zip.zip"
    files = ["two/hee", "hey", "missing_file"]
    folders = ["one/three", "else", "missing_dir"]

    zip_selected(work_path, work_dir.name, dest_zip, files, folders)

    unzip_dir = work_path / "unzip"
    unzip_archive(dest_zip, unzip_dir)

    assert dest_zip.exists()
    assert (unzip_dir / "test/four/hey").exists()
    assert (unzip_dir / "test/one/hey").exists()
    assert (unzip_dir / "test/one/three/now").exists()
    assert (unzip_dir / "test/something/else/altogether").exists()
    assert (unzip_dir / "test/two/hee").exists()
    assert search_caplog(caplog, "Zipping test/two/hee")
    assert search_caplog(caplog, "Looked for missing_file but")
    assert search_caplog(caplog, "Looked for missing_dir but")
