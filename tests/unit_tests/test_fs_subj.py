import logging
from pathlib import Path

FS_DIR = Path("/usr/local/freesurfer/")
SUBJECTS_DIR = Path(FS_DIR / "subjects")


log = logging.getLogger(__name__)


def test_fs_subj_works(caplog, install_gear):
    """Make sure license and subject get installed."""

    caplog.set_level(logging.DEBUG)

    install_gear("fs_subj.zip")

    assert (FS_DIR / "license.txt").exists()
    assert (SUBJECTS_DIR / "sub-TOME3024/mri/orig.mgz").exists()
