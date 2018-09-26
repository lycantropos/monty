ARG PYTHON3_VERSION

FROM python:${PYTHON3_VERSION}

WORKDIR /opt/monty

COPY template/ template/
COPY monty/ monty/
COPY tests/ tests/
COPY README.md .
COPY setup.py .
COPY setup.cfg .

RUN python3 -m pip install -e .
