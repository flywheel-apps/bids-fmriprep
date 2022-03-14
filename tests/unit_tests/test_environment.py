import logging

from run import get_and_log_environment

log = logging.getLogger(__name__)


def test_get_and_log_environment_works(caplog, search_caplog):

    caplog.set_level(logging.DEBUG)

    environ = get_and_log_environment()

    assert environ["FLYWHEEL"] == "/flywheel/v0"
    assert environ["FREESURFER_HOME"] == "/opt/freesurfer"
    assert search_caplog(caplog, "FREESURFER_HOME=/opt/freesurfer")
    assert search_caplog(
        caplog, "Grabbing environment from /flywheel/v0/gear_environ.json"
    )
