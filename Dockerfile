FROM nipreps/fmriprep:20.2.7

LABEL maintainer="support@flywheel.io"

ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Remove expired LetsEncrypt cert
RUN rm /usr/share/ca-certificates/mozilla/DST_Root_CA_X3.crt && \
    update-ca-certificates
ENV REQUESTS_CA_BUNDLE "/etc/ssl/certs/ca-certificates.crt"

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

COPY manifest.json ${FLYWHEEL}/manifest.json
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py
RUN chmod a+x ${FLYWHEEL}/run.py
COPY run.sh ${FLYWHEEL}/run.sh
RUN chmod a+x ${FLYWHEEL}/run.sh

# Set up python to run Flywheel SDK isolated from whatever is in the base image
RUN conda create -n py38 python=3.8.10 -c anaconda -y
RUN . /usr/local/miniconda/etc/profile.d/conda.sh && \
    conda activate py38 && \
    pip install --no-cache-dir -r $FLYWHEEL/requirements.txt

# Configure entrypoint (run.sh activates gear code environment then runs run.py)
ENTRYPOINT ["/flywheel/v0/run.sh"]
