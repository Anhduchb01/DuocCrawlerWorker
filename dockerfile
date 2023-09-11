# base image
FROM python:3.9.16

# set working directory
WORKDIR /usr/src/app
RUN pip install --upgrade pip
# add requirements (to leverage Docker cache)
COPY ./requirements.txt .

# install requirements
RUN pip install -r requirements.txt

# copy project
COPY . .
