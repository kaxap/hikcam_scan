FROM python:3.6
MAINTAINER kax
ENV PYTHONUNBUFFERED=1

COPY *.py *.txt *.yml ./
RUN pip install -r requirements.txt