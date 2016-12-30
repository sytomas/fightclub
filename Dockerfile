FROM ubuntu:14.04
MAINTAINER Syd Tomas <sytomas@cisco.com>
EXPOSE 10010

ENV SPARK_BOT_EMAIL=fightclub@sparkbot.io
ENV SPARK_BOT_TOKEN=MzJjZDAxNWUtOTIzZC00MTdmLTg0MWQtMjVkY2ZkNjU0ZmYxZDdjZDM1NjgtYWMw
ENV SPARK_BOT_URL=http://ec2-54-183-13-197.us-west-1.compute.amazonaws.com:10010
ENV SPARK_BOT_APP_NAME='fightclub'

RUN "sh" "-c" "echo nameserver 8.8.8.8 >> /etc/resolv.conf"

# install system-wide deps for python and node
RUN apt-get -yqq update
RUN apt-get -yqq install python-pip python-dev
RUN mkdir /opt/flask

WORKDIR /opt/flask
ADD requirements.txt /opt/flask
RUN pip install itty
RUN pip install -r /opt/flask/requirements.txt
Add . /opt/flask


# start app
CMD [ "python", "./bot.py" ]
