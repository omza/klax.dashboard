# Use the Python3.7.2 image
FROM python:3.8-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app 
ADD . /app

# Install the dependencies
RUN pip install --no-cache-dir --upgrade pip \
    pip install --no-cache-dir -r requirements.txt

# Local log location & Environments
# ----------------------------------------------------------
ENV DOCKER_PATH_LOG=/var/opt/klax
RUN mkdir -p ${DOCKER_PATH_LOG}

ENV PATH_LOG=${PATH_LOG} \
    LOG_FILE=${LOG_FILE} \
    LOG_LEVEL=${LOG_LEVEL} \
    END_DEVICE_ID=${END_DEVICE_ID} \
    DB_NAME=${DB_NAME} \
    USER_FIRSTNAME=${USER_FIRSTNAME} \
    USER_EMAIL=${USER_EMAIL} \
    USER_PASS=${USER_PASS} \
    MQTT_SERVICE=${MQTT_SERVICE} \
    MQTT_HOST=${MQTT_HOST} \
    MQTT_PORT=${MQTT_PORT} \
    MQTT_USER=${MQTT_USER} \
    MQTT_PASSWORD=${MQTT_PASSWORD} \
    MQTT_TOPIC=${MQTT_TOPIC} \
    FORWARDED_ALLOW_IPS={$FORWARDED_ALLOW_IPS}

#VOLUME
VOLUME ${DOCKER_PATH_LOG}

# run the command to start uvicorn
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "83"]
