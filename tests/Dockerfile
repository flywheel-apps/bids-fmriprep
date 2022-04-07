ARG DOCKER_IMAGE_NAME

FROM ${DOCKER_IMAGE_NAME}

RUN poetry install

COPY tests ./tests
RUN chmod +x ./tests/bin/poetry_test.sh

ENTRYPOINT ["/flywheel/v0/tests/bin/tests.sh"]
