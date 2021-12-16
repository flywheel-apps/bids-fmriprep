#! /usr/bin/env python3
"""Run bids-fmriprep on project "BIDS_multi_session"

    This script was created to run Job ID 61a92d907a4ab255b14ab511
    In project "bids-apps/BIDS_multi_session"
    On Flywheel Instance https://ga.ce.flywheel.io/api
    It has its input file attached to the project and this file makes fMIRPrep fail
"""

import argparse
import os
from datetime import datetime

import flywheel

input_files = {
    "bids-filter-file": {
        "container_path": "bids-apps/BIDS_multi_session",
        "location_name": "PyBIDS_filter.json",
    }
}


def main(fw):

    gear = fw.lookup("gears/bids-fmriprep")
    print("gear.gear.version in original job was = 1.2.2_20.2.6_rc4")
    print(f"gear.gear.version now = {gear.gear.version}")
    print("destination_id = 6151e90263e0a8412b4ec863")
    print("destination type is: project")
    destination = fw.lookup("bids-apps/BIDS_multi_session")

    inputs = dict()
    for key, val in input_files.items():
        container = fw.lookup(val["container_path"])
        inputs[key] = container.get_file(val["location_name"])

    config = {
        "anat-only": False,
        "aroma-melodic-dimensionality": -200,
        "boilerplate_only": False,
        "bold2t1w-dof": 6,
        "bold2t1w-init": "register",
        "cifti-output": False,
        "debug": "",
        "dvars-spike-threshold": 1.5,
        "echo-idx": "",
        "error-on-aroma-warnings": False,
        "fd-spike-threshold": 0.5,
        "fmap-bspline": False,
        "fmap-no-demean": False,
        "force-bbr": False,
        "force-no-bbr": False,
        "force-syn": False,
        "fs-no-reconall": False,
        "gear-FREESURFER_LICENSE": "",
        "gear-dry-run": False,
        "gear-intermediate-files": "",
        "gear-intermediate-folders": "",
        "gear-keep-fsaverage": False,
        "gear-keep-output": False,
        "gear-log-level": "INFO",
        "gear-run-bids-validation": False,
        "gear-save-intermediate-output": False,
        "ignore": "",
        "longitudinal": False,
        "lsf-cpu": "4",
        "lsf-ram": "rusage[mem=12000]",
        "md-only-boilerplate": False,
        "medial-surface-nan": False,
        "mem_mb": 0,
        "n_cpus": 0,
        "no-submm-recon": False,
        "notrack": False,
        "omp-nthreads": 0,
        "output-spaces": "MNI152NLin2009cAsym",
        "reports-only": False,
        "resource-monitor": False,
        "return-all-components": False,
        "singularity-debug": False,
        "skip-bids-validation": False,
        "skull-strip-fixed-seed": False,
        "skull-strip-t1w": "force",
        "skull-strip-template": "OASIS30ANTs",
        "stop-on-first-crash": False,
        "task-id": "",
        "use-aroma": False,
        "use-syn-sdc": False,
        "verbose": "",
        "write-graph": False,
    }

    now = datetime.now()
    analysis_label = (
        f'{gear.gear.name} {now.strftime("%m-%d-%Y %H:%M:%S")} SDK launched'
    )
    print(f"analysis_label = {analysis_label}")

    analysis_id = gear.run(
        analysis_label=analysis_label,
        config=config,
        inputs=inputs,
        destination=destination,
    )
    print(f"analysis_id = {analysis_id}")
    return analysis_id


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    fw = flywheel.Client("")
    print(fw.get_config().site.api_url)

    analysis_id = main(fw)

    os.sys.exit(0)
