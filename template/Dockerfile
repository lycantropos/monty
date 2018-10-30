ARG PYTHON_IMAGE
ARG PYTHON_IMAGE_VERSION

FROM ${PYTHON_IMAGE}:${PYTHON_IMAGE_VERSION}

WORKDIR /opt/__project__

COPY __project__/ __project__/
COPY tests/ tests/
COPY README.md .
COPY setup.py .
COPY setup.cfg .

RUN pip install -e .
