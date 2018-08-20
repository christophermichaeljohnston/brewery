FROM python:3
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y supervisor

ADD supervisord/brewery.conf /etc/supervisor/conf.d
ADD supervisord/brewery-tasks.conf /etc/supervisor/conf.d

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/
RUN pip install -r requirements.txt
