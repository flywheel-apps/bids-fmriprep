FROM nipreps/fmriprep:23.0.1

LABEL maintainer="support@flywheel.io"

ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Save docker environ here to keep it separate from the Flywheel gear environment
RUN python -c 'import os, json; f = open("/flywheel/v0/gear_environ.json", "w"); json.dump(dict(os.environ), f)'

RUN apt-get update && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y \
    time \
    zip \
    nodejs \
    tree && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g bids-validator@1.8.4 \
    esbuild@0.13.4 \
    esbuild-runner@2.2.1

COPY requirements.txt $FLYWHEEL/

# Set up python to run Flywheel SDK isolated from whatever is in the base image
RUN conda create -n py38 python=3.8.10 -c anaconda -y
RUN . /root/.bashrc && \
    conda init bash && \
    conda activate py38 && \
    pip install --no-cache-dir -r $FLYWHEEL/requirements.txt

COPY manifest.json ${FLYWHEEL}/manifest.json
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py
RUN chmod a+x ${FLYWHEEL}/run.py
COPY run.sh ${FLYWHEEL}/run.sh
RUN chmod a+x ${FLYWHEEL}/run.sh

# Configure entrypoint (run.sh activates gear code environment then runs run.py)
ENTRYPOINT ["/flywheel/v0/run.sh"]
