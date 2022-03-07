#! /usr/bin/env python3
"""Create a python script to re-run bids-fmriprep given the job ID for a gear
that was run on Flywheel.

Use the output of the previous job as input to the new job so it won't have
to re-do as much.

This was copied from 'copy-job.py'
"""

import argparse
import os
import sys
from datetime import datetime

import flywheel


def main(job_id):

    fw = flywheel.Client("")
    print("Flywheel Instance", fw.get_config().site.api_url)

    analysis = None
    if args.analysis:
        analysis = fw.get_analysis(job_id)
        print(f"Getting job_id from analysis '{analysis.label}'")
        job_id = analysis.job.id

    print("Job ID", job_id)
    job = fw.get_job(job_id)
    oldgear = fw.get_gear(job.gear_id)
    gear = fw.lookup("gears/bids-fmriprep")  # get current version in case gear inputs
    gear_name = oldgear.gear.name
    print(f"gear.gear.name is {gear_name}")
    if gear_name != "bids-fmriprep":
        print("Wat?  This script is to re-run fMRIPrep.  I quit.")
        sys.exit(1)
    destination_id = job.destination.id
    destination_type = job.destination.type
    print(f"job's destination_id is {destination_id} type {destination_type}")

    if job.destination.type == "analysis":
        analysis = fw.get_analysis(destination_id)
        destination_id = analysis.parent.id
        destination_type = analysis.parent.type
        print(f"job's analysis's parent id is {destination_id} type {destination_type}")
    else:
        print(
            "Wat?  This script is to re-run fMRIPrep.  The destination should be an analysis.  I quit."
        )
        sys.exit(1)

    destination = fw.get(destination_id)
    destination_label = destination.label
    print(f"new job's destination is {destination_label} type {destination_type}")

    inputs = dict()
    for key, val in job.config.get("inputs").items():
        if "hierarchy" in val:
            input_container = fw.get(val["hierarchy"]["id"])
            inputs[key] = input_container.get_file(val["location"]["name"])

    # Add output of job as input to new job
    file_name = "unknown"
    for ff in analysis.files:
        if ff.name.startswith("bids-fmriprep_") and not "_work_" in ff.name:
            file_name = ff.name
            inputs["previous-results"] = analysis.get_file(file_name)
            break

    if file_name == "unknown":
        print("Could not find zipped output of original bids-fmriprep job")
        sys.exit(1)

    config = job["config"]["config"]

    now = datetime.now()
    analysis_label = (
        f'{gear.gear.name} {now.strftime("%m-%d-%Y %H:%M:%S")} SDK re-launched'
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

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("job_id", help="Flywheel job ID")
    parser.add_argument(
        "-a",
        "--analysis",
        action="store_true",
        help="ID provided is for the analysis (job destination)",
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)

    args = parser.parse_args()

    main(args.job_id)

    os.sys.exit(0)
