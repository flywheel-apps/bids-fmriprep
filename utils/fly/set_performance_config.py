import logging
import os

import psutil

log = logging.getLogger(__name__)


def set_n_cpus(n_cpus, omp_nthreads):
    """Set --n_cpus (number of threads) to pass to BIDS App.

    Use the given number unless it is too big.  Use the max available if zero.

    The user may want to set these number to less than the maximum if using a
    shared compute resource.

    Args:
        n_cpus (int): number of cpus to use from config.json

    Returns:
        n_cpus (int) which will become part of the command line command
    """

    os_cpu_count = os.cpu_count()
    log.info("os.cpu_count() = %d", os_cpu_count)
    if n_cpus:
        if n_cpus > os_cpu_count:
            log.warning("n_cpus > number available, using max %d", os_cpu_count)
            n_cpus = os_cpu_count
        else:
            log.info("n_cpus using %d from config", n_cpus)
    else:  # Default is to use all cpus available
        n_cpus = os_cpu_count  # zoom zoom
        log.info("using n_cpus = %d (maximum available)", os_cpu_count)

    # Do the same for omp-nthreads
    if omp_nthreads:
        if omp_nthreads > os_cpu_count:
            log.warning("omp-nthreads > number available, using max %d", os_cpu_count)
            omp_nthreads = os_cpu_count
        else:
            log.info("omp-nthreads using %d from config", omp_nthreads)
    else:  # Default is to use all cpus available
        omp_nthreads = os_cpu_count  # zoom zoom
        log.info("using omp-nthreads = %d (maximum available)", os_cpu_count)

    return n_cpus, omp_nthreads


def set_mem_mb(mem_mb):
    """Set --mem (maximum memory to use in MB) to pass to BIDS App.

    Use the given number unless it is too big.  Use the max available if zero.

    The user may want to set these number to less than the maximum if using a
    shared compute resource.

    Args:
        mem_mb (float) number of MB to use

    Returns:
        mem_mb (float) which will become part of the command line command
    """

    psutil_mem_mb = int(psutil.virtual_memory().available / (1024 ** 2))
    log.info("psutil.virtual_memory().available= {:5.2f} MiB".format(psutil_mem_mb))
    if mem_mb:
        if mem_mb > psutil_mem_mb:
            log.warning("mem > number available, using max %d", psutil_mem_mb)
            mem_mb = psutil_mem_mb
        else:
            log.info("mem using %d from config", mem_mb)
    else:  # Default is to use all memory available
        mem_mb = psutil_mem_mb
        log.info("using mem = %d (maximum available)", psutil_mem_mb)

    return mem_mb
