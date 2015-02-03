
FROM python:2-onbuild
MAINTAINER Tomas Kral <tomas.kral@gmail.com>


EXPOSE 4000
ENTRYPOINT ["python", "web.py"]

