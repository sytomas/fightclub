FROM ubuntu:14.04
MAINTAINER Syd Tomas <sytomas@cisco.com>

# install system-wide deps for python and node
RUN apt-get -yqq update
RUN apt-get -yqq install python-pip python-dev

#ADD fightclub /home/ec2-user/code/fightclub
ADD fightclub /home/ec2-user/app
WORKDIR /home/ec2-user/app

COPY . /home/ec2-user/app
RUN pip install -r /home/ec2-user/app/requirements.txt

# expose port
EXPOSE 10010

# start app
CMD [ "python", "./bot.py" ]
