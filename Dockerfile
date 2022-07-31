FROM python:latest

ENV INSTALL_PATH /snakeeyes

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

RUN apt-get update
RUN apt-get -y install python3-pip python3-dev libpq-dev postgresql postgresql-contrib

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
COPY . .
RUN ls
RUN pip install --editable .
RUN ls
CMD gunicorn -b 0.0.0.0:8888 --access-logfile - "snakeeyes.app:create_app()"