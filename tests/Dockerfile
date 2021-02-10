ARG DOCKER_IMAGE_NAME

FROM ${DOCKER_IMAGE_NAME}

COPY tests ./tests

RUN pip install -r tests/requirements.txt

ENTRYPOINT ["/flywheel/v0/tests/bin/tests.sh"]
