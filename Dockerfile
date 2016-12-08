FROM ubuntu:14.04
MAINTAINER Syd Tomas <sytomas@cisco.com>
EXPOSE 10010

# install system-wide deps for python and node
RUN apt-get -yqq update
RUN apt-get -yqq install python-pip python-dev


#WORKDIR /home/ec2-user/app
WORKDIR /home/ec2-user/app
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
Add /home/ec2-user/code/fightclub/ /app/


# start app
CMD [ "python", "./bot.py" ]
