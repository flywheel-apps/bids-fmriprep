import json
import logging

import flywheel_gear_toolkit

from run import set_performance_config


def search_sysout(captured, find_me):
    """Search capsys message for find_me, return message"""
    for msg in captured.out.split("/n"):
        if find_me in msg:
            return msg
    return ""


def print_captured(captured):
    print("\nout")
    for ii, msg in enumerate(captured.out.split("\n")):
        print(f"{ii:2d} {msg}")
    print("\nerr")
    for ii, msg in enumerate(captured.err.split("\n")):
        print(f"{ii:2d} {msg}")


def search_stdout_contains(captured, find_me, contains_me):
    """Search stdout message for find_me, return true if it contains contains_me"""
    for msg in captured.out.split("/n"):
        if find_me in msg:
            print(f"Found '{find_me}' in '{msg}'")
            if contains_me in msg:
                print(f"Found '{contains_me}' in '{msg}'")
                return True
    return False


#
#  Tests
#


def test_set_performance_config_0_is_max(capfd):

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


def test_set_performance_config_2much_is_2much(capfd):

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


def test_set_performance_config_default_is_max(capfd):

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


def test_set_performance_config_1_is_1(capfd):

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
