ARG PYTHON_VERSION="3"

FROM python:${PYTHON_VERSION}

WORKDIR /opt/monty

COPY ./template template
COPY ./tests tests
COPY ./setup.py setup.py
COPY ./setup.cfg setup.cfg
COPY ./scripts scripts

RUN python3 -m pip install .
