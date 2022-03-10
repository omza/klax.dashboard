FROM python:3.8-buster

# Pip Install requirements
# ----------------------------------------------------------
COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt


# Copy docker context
# ----------------------------------------------------------
COPY . /opt/app

# Local log location
# ----------------------------------------------------------
ENV APPLICATION_LOG_PATH=/opt/app/log
RUN mkdir -p ${APPLICATION_LOG_PATH}

# Start/Stop
# -------------------------------------------------------
ENTRYPOINT ["python", "main.py"]
