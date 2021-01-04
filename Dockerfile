# Dockerfile-flask
FROM python:3.7
MAINTAINER Vishal


WORKDIR /connect4

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y vim

ADD . /connect4

EXPOSE 5025

CMD [ "uwsgi", "--ini", "app.ini"]