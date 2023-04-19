#!/bin/bash --login

# This run.sh is necessary to activate the gear code's python environment:
echo "In tests/bin/run.sh, checking python version"
python --version
#echo "RUNNING conda init bash"
#conda init bash
echo "RUNNING conda activate, python --version"
conda activate py38 && python --version
python --version
echo /flywheel/v0/tests/bin/tests.sh
/flywheel/v0/tests/bin/tests.sh
