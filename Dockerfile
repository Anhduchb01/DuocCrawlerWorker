# base image
FROM python:3.9.17-bullseye
RUN mkdir /app
# set working directory
WORKDIR /app
RUN pip install --upgrade pip
# add requirements (to leverage Docker cache)
COPY ./requirements.txt .

# install requirements
RUN pip install -r requirements.txt

# copy project
COPY . .
USER root
RUN chmod -R 777 /app/*
# CMD celery -A app.celery worker  --loglevel=info --pool=eventlet
CMD ["python", "app.py"]


