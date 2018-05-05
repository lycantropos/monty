ARG PYTHON3_VERSION

FROM python:${PYTHON3_VERSION}

WORKDIR /opt/__project__

COPY __project__/ __project__/
COPY tests/ tests/
COPY README.md .
COPY setup.py .
COPY setup.cfg .

RUN python3 -m pip install -e .
