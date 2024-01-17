# base image
FROM registry.apps.xplat.fis.com.vn/library/python:3.9.17-bullseye
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

# Define the default command to start your application
CMD ["celery", "-A", "crawler.celery", "worker", "--loglevel=info","--pool=eventlet"]
# CMD ["python", "app.py"]
