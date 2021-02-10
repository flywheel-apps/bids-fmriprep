FROM nipreps/fmriprep:20.2.1

LABEL maintainer="support@flywheel.io"

ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Save docker environ here to keep it separate from the Flywheel gear environment
RUN python -c 'import os, json; f = open("/flywheel/v0/gear_environ.json", "w"); json.dump(dict(os.environ), f)'

RUN apt-get update && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y \
    zip \
    nodejs \
    tree && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g bids-validator@1.5.7

# Python 3.7.1 (default, Dec 14 2018, 19:28:38)
# [GCC 7.3.0] :: Anaconda, Inc. on linux
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/pip

# Create symbolic link for Freesurfer license but delete the target because
# the gear's "freesurfer" directory will be created when the gear runs
RUN mkdir -p ${FLYWHEEL}/freesurfer
RUN touch ${FLYWHEEL}/freesurfer/license.txt
RUN ln -s ${FLYWHEEL}/freesurfer/license.txt /opt/freesurfer/license.txt
RUN rm -rf ${FLYWHEEL}/freesurfer

ENV PYTHONUNBUFFERED 1

# Copy executable/manifest to Gear
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py

# Configure entrypoint
RUN chmod a+x ${FLYWHEEL}/run.py
ENTRYPOINT ["/flywheel/v0/run.py"]
