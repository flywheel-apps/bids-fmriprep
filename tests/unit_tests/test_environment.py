import logging

from run import get_and_log_environment

log = logging.getLogger(__name__)


def test_get_and_log_environment_works(capfd, print_captured, search_stdout_contains):

    config = {"omp-nthreads": "4"}

    environ = get_and_log_environment(config, log)

    captured = capfd.readouterr()

    print_captured(captured)

    assert environ["OMP_NUM_THREADS"] == "4"
