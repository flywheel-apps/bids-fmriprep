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


def set_mem_gb(mem_gb):
    """Set --mem (maximum memory to usen in GB) to pass to BIDS App.

    Use the given number unless it is too big.  Use the max available if zero.

    The user may want to set these number to less than the maximum if using a
    shared compute resource.

    Args:
        mem_gb (float) number of GiB to use

    Returns:
        mem_gb (float) which will become part of the command line command
    """

    psutil_mem_gb = int(psutil.virtual_memory().available / (1024 ** 3))
    log.info("psutil.virtual_memory().available= {:5.2f} GiB".format(psutil_mem_gb))
    if mem_gb:
        if mem_gb > psutil_mem_gb:
            log.warning("mem > number available, using max %d", psutil_mem_gb)
            mem_gb = psutil_mem_gb
        else:
            log.info("mem using %d from config", mem_gb)
    else:  # Default is to use all memory available
        mem_gb = psutil_mem_gb
        log.info("using mem = %d (maximum available)", psutil_mem_gb)

    return mem_gb
