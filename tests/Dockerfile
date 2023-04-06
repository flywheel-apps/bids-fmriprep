ARG DOCKER_IMAGE_NAME

FROM ${DOCKER_IMAGE_NAME}

COPY requirements-dev.txt $FLYWHEEL/

RUN . /usr/local/miniconda/etc/profile.d/conda.sh && \
    conda activate py38 && \
    pip install --no-cache-dir -r $FLYWHEEL/requirements-dev.txt

# Activate conda in py38 whenever this container is started
Run echo ". /usr/local/miniconda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate py38" >> ~/.bashrc

COPY tests ./tests

ENTRYPOINT ["/flywheel/v0/tests/bin/tests.sh"]
