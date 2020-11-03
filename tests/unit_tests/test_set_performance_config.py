import json
import logging

import flywheel_gear_toolkit

from run import set_performance_config


def test_set_performance_config_0_is_max(capfd, print_captured, search_stdout_contains):

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:
        gtk_context.init_logging("info")
        gtk_context.log_config()
        log = gtk_context.log

        config = {"n_cpus": 0, "mem_mb": 0}

        set_performance_config(config, log)

    print("config = ", json.dumps(config, indent=4))

    captured = capfd.readouterr()

    print_captured(captured)

    assert search_stdout_contains(captured, "using n_cpus", "maximum available")
    assert search_stdout_contains(captured, "using mem_mb", "maximum available")


def test_set_performance_config_2much_is_2much(capfd, search_sysout, print_captured):

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:
        gtk_context.init_logging("info")
        gtk_context.log_config()
        log = gtk_context.log

        config = {"n_cpus": 10001, "mem_mb": 100001}

        set_performance_config(config, log)

    print("config = ", json.dumps(config, indent=4))

    captured = capfd.readouterr()

    print_captured(captured)

    assert search_sysout(captured, "n_cpus > number")
    assert search_sysout(captured, "mem_mb > number")


def test_set_performance_config_default_is_max(
    capfd, print_captured, search_stdout_contains
):

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:
        gtk_context.init_logging("info")
        gtk_context.log_config()
        log = gtk_context.log

        config = {}

        set_performance_config(config, log)

    print("config = ", json.dumps(config, indent=4))

    captured = capfd.readouterr()

    print_captured(captured)

    assert search_stdout_contains(captured, "using n_cpus", "maximum available")
    assert search_stdout_contains(captured, "using mem_mb", "maximum available")


def test_set_performance_config_1_is_1(capfd, search_sysout, print_captured):

    with flywheel_gear_toolkit.GearToolkitContext(input_args=[]) as gtk_context:
        gtk_context.init_logging("info")
        gtk_context.log_config()
        log = gtk_context.log

        config = {"n_cpus": 1, "mem_mb": 1}

        set_performance_config(config, log)

    print("config = ", json.dumps(config, indent=4))

    captured = capfd.readouterr()

    print_captured(captured)

    assert config["n_cpus"] == 1
    assert config["mem_mb"] == 1
    assert search_sysout(captured, "from config")
