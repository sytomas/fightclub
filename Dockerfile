FROM ubuntu:14.04
MAINTAINER Syd Tomas <sytomas@cisco.com>
EXPOSE 10010

# install system-wide deps for python and node
RUN apt-get -yqq update
RUN apt-get -yqq install python-pip python-dev
RUN mkdir /opt/flask

WORKDIR /opt/flask
ADD requirements.txt /opt/flask
RUN pip install -r /requirements.txt
Add . /opt/flask


# start app
CMD [ "python", "./bot.py" ]
