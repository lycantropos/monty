ARG PYTHON_IMAGE
ARG PYTHON_IMAGE_VERSION

FROM ${PYTHON_IMAGE}:${PYTHON_IMAGE_VERSION}

RUN pip install --upgrade pip setuptools

WORKDIR /opt/_project_

COPY requirements.txt .
RUN pip install --force-reinstall -r requirements.txt

COPY requirements-tests.txt .
RUN pip install --force-reinstall -r requirements-tests.txt

COPY README.md .
COPY setup.cfg .
COPY setup.py .
COPY _project_ _project_/
COPY tests/ tests/
