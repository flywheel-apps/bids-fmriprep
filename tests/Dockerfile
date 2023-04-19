ARG DOCKER_IMAGE_NAME

FROM ${DOCKER_IMAGE_NAME}

COPY requirements-dev.txt $FLYWHEEL/

RUN . /root/.bashrc && \
    conda init bash && \
    conda activate py38 && \
    pip install --no-cache-dir -r $FLYWHEEL/requirements-dev.txt

# Activate conda in py38 whenever this container is started
Run echo "conda init bash" >> ~/.bashrc
Run echo "conda activate py38" >> ~/.bashrc

COPY tests ./tests

ENTRYPOINT ["/flywheel/v0/tests/bin/run.sh"]
