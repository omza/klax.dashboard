# Use the Python3.7.2 image
FROM python:3.8-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app 
ADD . /app

# Install the dependencies
RUN pip install -r requirements.txt

# Local log location
# ----------------------------------------------------------
ENV APPLICATION_LOG_PATH=/opt/app/log
RUN mkdir -p ${APPLICATION_LOG_PATH}

# run the command to start uWSGI
EXPOSE 5000
CMD ["uwsgi", "uwsgi.ini"]
