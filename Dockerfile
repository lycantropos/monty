FROM python:3

WORKDIR /monty
COPY . /monty/
RUN python3 -m pip install .
