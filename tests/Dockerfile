ARG DOCKER_IMAGE_NAME

FROM ${DOCKER_IMAGE_NAME}

COPY requirements-dev.txt $FLYWHEEL/
RUN pip install --no-cache-dir -r $FLYWHEEL/requirements-dev.txt

COPY tests ./tests

ENTRYPOINT ["/flywheel/v0/tests/bin/tests.sh"]
