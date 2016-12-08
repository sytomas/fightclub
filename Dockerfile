FROM ubuntu:14.04

# install system-wide deps for python and node
RUN apt-get -yqq update
RUN apt-get -yqq install python-pip python-dev

#ADD fightclub /home/ec2-user/code/fightclub
ADD fightclub /home/ec2-user/code
# WORKDIR /opt/flask-app
WORKDIR /opt/dock-image

COPY . /opt/dock-image
RUN pip install -r requirements.txt

# expose port
EXPOSE 10010

# start app
CMD [ "python", "./bot.py" ]
