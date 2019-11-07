ARG PYTHON_IMAGE
ARG PYTHON_IMAGE_VERSION

FROM ${PYTHON_IMAGE}:${PYTHON_IMAGE_VERSION}

RUN pip install --upgrade pip setuptools

WORKDIR /opt/monty

COPY template/ template/
COPY monty/ monty/
COPY tests/ tests/
COPY README.md .
COPY requirements.txt .
COPY requirements-tests.txt .
COPY setup.py .
COPY setup.cfg .

RUN pip install --force-reinstall -r requirements.txt
RUN pip install --force-reinstall -r requirements-tests.txt
