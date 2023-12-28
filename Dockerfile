# base image
FROM python:3.9.17-bullseye

# Install Telnet
RUN apt-get update && apt-get install -y telnet
RUN mkdir -p /.cache && echo "hello" > /.cache/hello.txt
RUN cat /.cache/hello.txt


# Create app directory
RUN mkdir /app

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Add requirements (to leverage Docker cache)
COPY ./requirements.txt .

# Install requirements
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Set permissions (if needed)
USER root
RUN chmod -R 777 /app/*
RUN chmod -R 777 /.cache/*

# Define the default command to start your application
CMD ["celery", "-A", "app.celery", "worker", "--loglevel=info","--pool=eventlet"]
# CMD ["python", "app.py"]
