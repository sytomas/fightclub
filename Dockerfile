FROM ubuntu:14.04

# install system-wide deps for python and node
RUN apt-get -yqq update
RUN apt-get -yqq install python-pip python-dev

ADD fightclub /home/ec2-user/code/fightclub
# WORKDIR /opt/flask-app

RUN sudo pip install -r requirements.txt

# expose port
EXPOSE 10010

# start app
CMD [ "python", "./bot.py" ]
