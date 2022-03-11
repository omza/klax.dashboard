""" imports & globals """
import signal
import time
from config import config, logging
#from db import init_worker_db
#from db.models import ConnectorType, Devices, Connector
import paho.mqtt.client as mqtt



# Handle gentle termination
stopsignal = False


def handler_stop_signals(signum, frame):
    """ handle sigterm and sigint """
    global stopsignal
    stopsignal = True


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(config.MQTT_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))



def main():
    """ Main program 
    """
    logging.info('----------------------------------------------------------')
    logging.info(f'worker service start main ....')
    logging.debug(f'... running in environment {config}')

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.tls_set()
    client.username_pw_set(username=config.MQTT_USER, password=config.MQTT_PASSWORD)


    client.connect(config.MQTT_HOST, config.MQTT_PORT)
    client.loop_start()



    # Init worker database and collect sessionmakers list
#    sessionsmakers = []
#    worker_sessionmaker = init_worker_db()
    #sessionsmakers.append(worker_sessionmaker)
#    worker_session = worker_sessionmaker()   

    # Create Demo Objects
#    if config.DEMO_MODE:
#        create_demo_objects(worker_session)    

    # Close all Sessions
#    worker_session.close()

    """ run until stopsignal"""
    while not stopsignal:
        time.sleep(1)

    """ goodby """
    # Close all Sessions
#    for sessionmaker in sessionsmakers:
#        sessionmaker.close_all()

    client.loop_stop()

    logging.info('worker service service terminated. Goodby!')
    logging.info('-----------------------------------------------------------')


""" run main if not imported """
if __name__ == '__main__':
    main()
