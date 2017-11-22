ARG PYTHON3_VERSION="3"

FROM python:${PYTHON3_VERSION}

WORKDIR /opt/__project__

COPY ./__project__ __project__
COPY ./tests tests
COPY ./setup.py setup.py
COPY ./setup.cfg setup.cfg

RUN python3 -m pip install .
