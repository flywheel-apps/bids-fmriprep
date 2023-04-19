#!/usr/bin/env bash

set -eu
unset CDPATH

USAGE="
Usage:
    $0 [OPTION...] [[--] PYTEST_ARGS...]
Runs all tests and linting.
Assumes running in test container or that flywheel_migration and all of its
dependencies are installed.
Options:
    -h, --help              Print this help and exit
    -s, --shell             Enter shell instead of running tests
    -- PYTEST_ARGS          Arguments passed to py.test
"


main() {
    export PYTHONDONTWRITEBYTECODE=1
    export PYTHONPATH=.

    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                log "$USAGE"
                exit 0
                ;;
            -s|--shell)
                sh
                exit
                ;;
            --)
                shift
                break
                ;;
            *)
                break
                ;;
        esac
        shift
    done

    WD="$( dirname "$0" )/../.."
    echo "WD is $WD"
    cd $WD

    # if running in Singularity, do all work in a temp directory
    if [[ -v SINGULARITY_NAME ]]; then
        echo "SINGULARITY_NAME is $SINGULARITY_NAME"
    elif [[ $(grep docker /proc/self/cgroup) ]]; then
        echo "Running in Docker"
    else
        echo "NOT running in Docker or Singularity"
    fi
    echo "Working directory is $WD"

    if [ ! -w "." ]; then
        log "INFO: NOT Cleaning pyc and previous coverage results (not writeable)"
    	COV=""
    else
        log "INFO: Cleaning pyc and previous coverage results ..."
        find . -type d -name __pycache__ -exec rm -rf {} \; || true
        find . -type f -name '*.pyc' -delete
        rm -rf .coverage htmlcov
    	COV="--cov=run --cov-report="
    fi

    python -m pytest tests/unit_tests tests/integration_tests --exitfirst $COV  "$@"

    if [ -w "." ]; then
        log "INFO: Reporting coverage ..."
        local COVERAGE_ARGS="--skip-covered"
        coverage report --show-missing $COVERAGE_ARGS
        coverage html $COVERAGE_ARGS
    fi
}

log() {
    printf "\n%s\n" "$@" >&2
}


main "$@"
