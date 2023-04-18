#!/bin/bash --login

# This run.sh is necessary to activate the gear code's python environment:
echo "in run.sh"
echo "python --version says"
python --version
echo conda activate py38
conda activate py38
echo "python --version says"
python --version
echo ./run.py
./run.py
