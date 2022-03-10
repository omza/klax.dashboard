""" imports & globals """
import signal
import schedule
import time
from config import config, logging
from db import init_worker_db
from db.models import ConnectorType, Devices, Connector
from connectors.elementiotconnector import (
    init_elementiot_db,
    merge_devices_from_elementiot,
    poll_readings_from_elementiot)

from logic.common import rollout_timeseries_all, poll_readings, merge_devices, create_demo_objects #, classify_measurements

# Handle gentle termination
stopsignal = False


def handler_stop_signals(signum, frame):
    """ handle sigterm and sigint """
    global stopsignal
    stopsignal = True


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)


def main():
    """ Main program for speedomat worker
        Instantiate and start schedules for pulling Measurements and
        Speedfreaks from various connectors
    """
    logging.info('----------------------------------------------------------')
    logging.info(f'worker service start main ....')
    logging.debug(f'... running in environment {config}')

    # Init worker database and collect sessionmakers list
    sessionsmakers = []
    worker_sessionmaker = init_worker_db()
    #sessionsmakers.append(worker_sessionmaker)
    worker_session = worker_sessionmaker()   

    # Create Demo Objects
    if config.DEMO_MODE:
        create_demo_objects(worker_session)    

    # Close all Sessions
    worker_session.close()

    # Roll Out TimeSeries on startup and schedule it every day
    logging.info(f'rollout timeseries....')
    rollout_timeseries_all()
    schedule.every().day.at("23:30").do(
        rollout_timeseries_all
    )
    logging.info(f'rollout timeseries done and scheduled....')

    # Merge devices
    logging.info(f'merge outstanding devices....')
    merge_devices()
    schedule.every(config.SCHEDULE_MERGE_DEVICES).minutes.do(
       merge_devices 
    )
    logging.info(f'merge outstanding devices done and scheduledevery {config.SCHEDULE_MERGE_DEVICES} minute!')    

    # Schedule polling readings
    poll_readings()
    logging.info(f'poll outstanding readings....')    
    schedule.every(config.SCHEDULE_PULL_READINGS).minutes.do(
        poll_readings
    )
    logging.info(f'polling measurements from devices done and scheduled every {config.SCHEDULE_PULL_READINGS} minute!')

    """ run until stopsignal """
    while not stopsignal:
        schedule.run_pending()
        time.sleep(1)

    """ goodby """
    # Close all Sessions
    for sessionmaker in sessionsmakers:
        sessionmaker.close_all()

    logging.info('worker service service terminated. Goodby!')
    logging.info('-----------------------------------------------------------')


""" run main if not imported """
if __name__ == '__main__':
    main()
