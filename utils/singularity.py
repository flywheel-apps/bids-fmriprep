"""Do what it takes to be able to run gears in Singularity.
"""

import logging
import os
import re
import shutil
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)


FWV0 = "/flywheel/v0"
SCRATCH_NAME = "gear-temp-dir-"


def run_in_tmp_dir(writable_dir):
    """Copy gear to a temporary directory and cd to there.

    Args:
        writable_dir (string): directory to use for temporary files if /flywheel/v0 is not
            writable.

    Returns:
        tmp_path (path) The path to the temporary directory so it can be deleted
    """

    running_in = ""

    # This just logs some info.  Leaving it here in case it might be useful.
    if "SINGULARITY_NAME" in os.environ:
        running_in = "Singularity"
        log.debug("SINGULARITY_NAME is %s", os.environ["SINGULARITY_NAME"])

    else:
        cgroup = Path("/proc/self/cgroup")
        if cgroup.exists():
            with open("/proc/self/cgroup") as fp:
                for line in fp:
                    if re.search("/docker/", line):
                        running_in = "Docker"
                        break

    if running_in == "":
        log.debug("NOT running in Docker or Singularity")
    else:
        log.debug("Running in %s", running_in)

    try:
        _ = tempfile.mkdtemp(prefix=SCRATCH_NAME, dir=FWV0)
        os.chdir(FWV0)  # run in /tmp/... directory so it is writeable
        log.debug("Running in %s", FWV0)
        return None
    except OSError as e:
        log.debug("Problem writing to %s: %s", FWV0, e.strerror)

    # This used to remove any previous runs (possibly left over from previous testing) but that would be bad
    # if other bids-fmripreps are running on shared hardware at the same time because their directories would
    # be deleted mid-run.  A very confusing error to debug!

    # Create temporary place to run gear
    WD = tempfile.mkdtemp(prefix=SCRATCH_NAME, dir=writable_dir)
    log.debug("Gear scratch directory is %s", WD)

    new_FWV0 = Path(WD + FWV0)
    new_FWV0.mkdir(parents=True)
    abs_path = Path(".").resolve()
    names = list(Path(FWV0).glob("*"))
    for name in names:
        if name.name == "gear_environ.json":  # always use real one, not dev
            (new_FWV0 / name.name).symlink_to(Path(FWV0) / name.name)
        else:
            (new_FWV0 / name.name).symlink_to(abs_path / name.name)
    os.chdir(new_FWV0)  # run in /tmp/... directory so it is writeable
    log.debug("cwd is %s", Path.cwd())

    return new_FWV0
