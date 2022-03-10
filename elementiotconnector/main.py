""" Read configuration from environment """
from config import config, log

""" imports"""
from elementiot.api import ApiDevice, Api, ApiFolder
from db import dbengine, Session
from db.models import Device, Reading

import time
import signal

""" globals """


if __name__ == "__main__":
    """ Main """

    log.info('elementiotconnector start up....')
    log.info('Logs are in: {}'.format(config.FULL_PATH_LOG))
    log.debug('DB Connection String: {}'.format(config.MYSQL_DATABASE_URI))
    log.debug('Initial Timestamp: {} and authkey: {}'.format(config.ELEMENTIOT_START_AT, config.ELEMENTIOT_API_KEY))
    log.info('-----------------------------------------------------------------------------------------------------')

    """ retrieve API Object """
    api = Api(config.ELEMENTIOT_API_KEY)

    if api.isconnected:

        # Get the parsers configured in db
        parsers = api.getparserids()
        log.debug('Parsers {} are retrieved'.format(parsers))

        # Get the folders configured in db
        folders = api.getfolderids()

        for folderid in folders:
            folder = ApiFolder(config.ELEMENTIOT_API_KEY,folderid)
            folder.pulldevices(parsers) # Pull all devices for each folder

        log.debug('Folders {} are retrieved'.format(folders))


        """ retrieve all devices configured """
        query = api.getdeviceids()
        alldevices = []

        log.info('Start communication with element iot for each device in list: {} ...'.format(query))
        for deviceid in query:

            device = ApiDevice(config.ELEMENTIOT_API_KEY, deviceid)
            # device found in elementiot and is merged with db
            if device.id:
                # start listening
                device.start_listening(30)
                # fill list
                alldevices.append(device.id)
                log.info('listen to device {} from timestamp: {} ...'.format(device.slug, device.last_message_at))

            #instance = None
            device = None

        log.info('communication to {} devices initiated!'.format(len(alldevices)))
        log.info('-----------------------------------------------------------------------------------------------------')


        try:
            """ run until exception
                to check new devices exists
            """
            while True:

                if api.isconnected:

                    # Get the parsers configured in db
                    parsers = api.getparserids()
                    log.debug('Parsers {} are retrieved'.format(parsers))

                    # Get the folders configured in db
                    folders = api.getfolderids()

                    for folderid in folders:
                        folder = ApiFolder(config.ELEMENTIOT_API_KEY,folderid)
                        folder.pulldevices(parsers) # Pull all devices for each folder

                    log.debug('Folders {} are retrieved'.format(folders))

                    # Get devices
                    query = api.getdeviceids()

                    for deviceid in query:
                        if deviceid not in alldevices:
                            log.info('new device {} detected...'.format(deviceid))
                            device = ApiDevice(config.ELEMENTIOT_API_KEY, deviceid)
                            # device found in elementiot and is merged with db
                            if device.id:
                                # start listening
                                device.start_listening(30)
                                # fill list
                                alldevices.append(device.id)
                                log.info('listen to device {} from timestamp: {} ...'.format(device.slug, device.last_message_at))

                log.debug('Waiting for new devices...')
                time.sleep(60)

        except Exception as e: # clean up at any exeption
            log.error(str(e))

        finally:

            """ goodby """
            for device in alldevices:
                device.stop_listening()

    else:

        log.info('elementiotconnector service terminated. Goodby!')
        log.info('-----------------------------------------------------------------------------------------------------')
