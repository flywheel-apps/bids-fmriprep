import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

FWV0 = Path.cwd()


def get_and_log_environment():
    """Grab and log environment to use when executing command lines.

    The shell environment is saved into a file at an appropriate place in the Dockerfile.

    Returns: environ (dict) the shell environment variables
    """
    environment_file = FWV0 / "gear_environ.json"
    log.debug("Grabbing environment from %s", environment_file)

    with open(environment_file, "r") as f:
        environ = json.load(f)

        # Add environment to log if debugging
        kv = ""
        for k, v in environ.items():
            kv += k + "=" + v + " "
        log.debug("Environment: " + kv)

    return environ
