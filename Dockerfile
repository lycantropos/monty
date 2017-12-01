ARG PYTHON3_VERSION

FROM python:${PYTHON3_VERSION}

WORKDIR /opt/monty

COPY template/ template/
COPY tests/ tests/
COPY README.rst .
COPY setup.py .
COPY setup.cfg .
COPY scripts/ scripts/

RUN python3 -m pip install -e .
