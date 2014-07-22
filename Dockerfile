
FROM ubuntu:trusty

MAINTAINER Tomas Kral <tomas.kral@gmail.com>

RUN apt-get update
RUN apt-get install -y python-pip python-dev

ADD . /opt/web

RUN pip install -r /opt/web/requirements.txt

EXPOSE 4000
ENTRYPOINT ["/usr/bin/python", "/opt/web/web.py"]

