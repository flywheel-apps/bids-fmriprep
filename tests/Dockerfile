ARG DOCKER_IMAGE_NAME

FROM ${DOCKER_IMAGE_NAME}

COPY requirements-dev.txt $FLYWHEEL/

RUN . /usr/local/miniconda/etc/profile.d/conda.sh && \
    conda activate py38 && \
    pip install --no-cache-dir -r $FLYWHEEL/requirements-dev.txt && \
    pip --version && \
    pip list > $FLYWHEEL/pip_list_test.txt

COPY tests ./tests

ENTRYPOINT ["/flywheel/v0/tests/bin/tests.sh"]
