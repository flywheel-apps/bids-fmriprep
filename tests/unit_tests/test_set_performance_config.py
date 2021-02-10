import logging

from utils.fly.set_performance_config import set_mem_gb, set_n_cpus


def test_set_performance_config_0_is_max(caplog, print_caplog, search_caplog_contains):

    caplog.set_level(logging.DEBUG)

    n_cpus, omp_nthreads = set_n_cpus(0, 0)
    mem_gb = set_mem_gb(0)

    print_caplog(caplog)

    assert search_caplog_contains(caplog, "using n_cpus", "maximum available")
    assert search_caplog_contains(caplog, "using omp-nthreads", "maximum available")
    assert search_caplog_contains(caplog, "using mem", "maximum available")


def test_set_performance_config_2much_is_2much(caplog, print_caplog, search_caplog):

    caplog.set_level(logging.DEBUG)

    n_cpus, omp_nthreads = set_n_cpus(10001, 10001)
    mem_gb = set_mem_gb(100001)

    print_caplog(caplog)

    assert search_caplog(caplog, "n_cpus > number")
    assert search_caplog(caplog, "omp-nthreads > number")
    assert search_caplog(caplog, "mem > number")


def test_set_performance_config_default_is_max(
    caplog, print_caplog, search_caplog_contains
):

    caplog.set_level(logging.DEBUG)

    n_cpus, omp_nthreads = set_n_cpus(None, None)
    mem_gb = set_mem_gb(None)

    print_caplog(caplog)
    print_caplog(caplog)

    assert search_caplog_contains(caplog, "using n_cpus", "maximum available")
    assert search_caplog_contains(caplog, "using omp-nthreads", "maximum available")
    assert search_caplog_contains(caplog, "using mem", "maximum available")


def test_set_performance_config_1_is_1(caplog, search_caplog, print_caplog):

    caplog.set_level(logging.DEBUG)

    n_cpus, omp_nthreads = set_n_cpus(1, 2)
    mem_gb = set_mem_gb(1)

    print_caplog(caplog)

    assert n_cpus == 1
    assert omp_nthreads == 2
    assert mem_gb == 1
    assert search_caplog(caplog, "from config")
