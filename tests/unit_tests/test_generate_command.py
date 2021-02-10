import json
import logging
from pathlib import Path

import flywheel_gear_toolkit

from run import generate_command


def test_generate_command_missing_config_works(
    capfd, print_captured, search_stdout_contains
):

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:
        gtk_context.init_logging("info")
        gtk_context.log_config()
        log = gtk_context.log

        config = {
            "bids_app_args": "arg1 arg2 bad_arg",
            "bool-param": False,
            "num-things": 42,
            "threshold": 3.1415926,
            "n_procs": 1,
            "verbose": "v",
            "write-graph": False,
            "gear-abort-on-bids-error": False,
            "gear-log-level": "INFO",
            "gear-run-bids-validation": False,
            "gear-save-intermediate-output": False,
            "gear-dry-run": True,
            "gear-keep-output": False,
            "n_cpus": 11,
            "mgm_gb": 12,
        }
        config = {}

        errors = []
        warnings = []

        generate_command(config, Path("work"), Path("out/###"), errors, warnings)

    captured = capfd.readouterr()

    print_captured(captured)

    assert search_stdout_contains(captured, "command is:", "out/##")

    # command is: ['./tests/test.sh', '/flywheel/v0/work/bids', '/flywheel/v0/output/5ebbfe82bfda51026d6aa079', 'participant', 'arg1', 'arg2', 'bad_arg', '--num-things=42', '--threshold=3.1415926', '--n_procs=1', '-v', '--n_cpus=11', '--mgm_gb=12']
