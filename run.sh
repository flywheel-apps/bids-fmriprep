#!/usr/bin/env bash

# This run.sh is necessary to activate the gear code's python environment:
. /usr/local/miniconda/etc/profile.d/conda.sh
conda activate py38
./run.py
