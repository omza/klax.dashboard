""" imports"""
import requests
import time
import threading

from config import config, log
from db import dbengine, Session
from db.models import Device, Reading, Parser, Folder, Apikey

from sqlalchemy.orm import sessionmaker


"""
    ElementIot API Calls

    Websockets (Readings & Packets):
    - wss://element-iot.com/api/v1/devices/<device-id>/readings/socket?auth=<authkey>
    - wss://element-iot.com/api/v1/devices/<device-id>/packets/socket?auth=<authkey>

    RESTful API
    - https://element-iot.com/api/v1/devices/<device-id>?auth=<authkey>  (Device Information)
    - https://element-iot.com/api/v1/devices/<device-id>/packets?<params>&auth=<authkey> (Packets)
    - https://element-iot.com/api/v1/devices/<device-id>/readings?<params>&auth=<authkey> (Packets)

    - Query String Parameters
        - limit	10	Amount of list items to retrieve. Defaults to 10. Must be a valid integer between 0 and 100.
        - sort	name	Property on the paginated item to sort by. Defaults to inserted_at if not stated otherwise.
        - sort_direction	ascending	Direction of the sort defined in the sort parameter. Can be either ascending or descending. Defaults to descending.
        - retrieve_after	881af0c9-72c2-4758-af09-4901bef0c15c	ID of the last paginated item from where to paginate from depending on the sort and sort_direction parameters. For example: if sort=inserted_at and sort_direction=descending, then only items older than the item with the specified ID will be returned.
        - before	2017-09-05T13:46:47.956173Z	Return only items that were created before a certain time. Allowed date types are listed below.
        - after	2017-09-04T03:12:02.882313Z	Return only items that were created after a certain time. Allowed date types are listed below.

"""

def RestRequestBody(url, authkey, retrieve_after_id='', after=''):
    """
        request element-iot RestApi
    """

    uri = url
    params = dict()

    if retrieve_after_id != '':
        params.update(
            limit=100,
            retrieve_after=retrieve_after_id,
            sort='inserted_at',
            sort_direction='ascending',
            auth=authkey
        )
    elif after != '':
        params.update(
            limit=100,
            after=after,
            sort='inserted_at',
            sort_direction='ascending',
            auth=authkey
        )
    else:
        params.update(auth=authkey)

    resp = requests.get(url=uri, params=params)
    data = resp.json()
    log.debug('Request to: {}'.format(resp.request.url))

    #Check Response
    if 'body' in data.keys():
        if 'retrieve_after_id' in data.keys():
            return data['body'], data['retrieve_after_id']
        else:
            return data['body'], None
    else:
        log.error('Request to {} faild because {}'.format(resp.request.url, data))
        return None, None


class Api(object):
    """
        represent the element-IOT RestAPI endpoints for folders, parsers, devices and API-Keys
        MERGED with the configured instances within the connector db
    """

    def __init__(self, authkey):

        self.__authkey = authkey
        self.__folderids = []
        self.__parserids = []
        self.__deviceids = []

        # if self.__mergeapikey__():
        self.isconnected = True
        # else:
        #    self.isconnected = False

    def __mergeapikey__(self):
        """ retreive apikey representation from element-iot and merge it with db """
        url="https://element-iot.com/api/v1/api_keys"

        # get data from elementiot
        listdata = self.__RestRequestBody__(url)

        # insert/merge into db
        for data in listdata:

            if data['key'] == self.__authkey:

                apikey = Apikey(
                                id = data['id'],
                                inserted_at = data['inserted_at'],
                                updated_at = data['updated_at'],
                                valid_until = data['valid_until'],
                                mandate_id = data['mandate_id'],
                                name = data['name'],
                                key = data['key'],
                                role = data['role'],
                                rate_scale = data['rate_scale'],
                                rate_limit = data['rate_limit']
                                )

                # Merge DB with element
                #
                session = Session()
                dbapikey = session.query(Apikey).filter_by(key=self.__authkey).first()
                if dbapikey:
                    dbapikey = session.merge(apikey)

                else:
                    dbapikey = session.add(apikey)

                session.commit()

                return True

            else:
                return False

        return False

    def __mergefolder__(self, folderid):
        """ retreive folder representation from element-iot and merge it with db """
        url="https://element-iot.com/api/v1/tags/" + folderid

        # get data from elementiot
        data = self.__RestRequestBody__(url)

        # insert/merge into db
        if data:

            folder = Folder(
                            id = data['id'],
                            inserted_at = data['inserted_at'],
                            updated_at = data['updated_at'],
                            mandate_id = data['mandate_id'],
                            name = data['name'],
                            slug = data['slug'],
                            description = data['description']
                            )

            # Merge DB with element
            #
            session = Session()
            dbfolder = session.query(Folder).filter_by(id=folderid).first()
            if dbfolder:
                dbfolder = session.merge(folder)

            else:
                dbfolder = session.add(folder)

            session.commit()

            return True

        else:
            return False

    def __mergeparser__(self, parserid):
        """ retreive parser representation from element-iot and merge it with db """
        url="https://element-iot.com/api/v1/parsers/" + parserid

        # get data from elementiot
        data = self.__RestRequestBody__(url)

        # insert/merge into db
        if data:

            parser = Parser(
                            id = data['id'],
                            inserted_at = data['inserted_at'],
                            updated_at = data['updated_at'],
                            mandate_id = data['mandate_id'],
                            name = data['name']
                            )

            # Merge DB with element
            #
            session = Session()
            dbparser = session.query(Parser).filter_by(id=parserid).first()
            if dbparser:
                dbparser = session.merge(parser)

            else:
                dbparser = session.add(parser)

            session.commit()

            return True

        else:
            return False

    def __mergedevice__(self, deviceid):
        """ retreive parser representation from element-iot and merge it with db
            test git
        """
        url='https://element-iot.com/api/v1/devices/' + deviceid

        # get data from elementiot
        data = self.__RestRequestBody__(url)

        # insert/merge into db
        if data:
            device = Device(
                            id = data['id'],
                            inserted_at = data['inserted_at'],
                            updated_at = data['updated_at'],
                            static_location = data['static_location'],
                            slug = data['slug'],
                            name = data['name'],
                            location = data['location']
                            )

            # Merge DB with element
            #
            session = Session()
            dbdevice = session.query(Device).filter_by(id=deviceid).first()
            if dbdevice:
                device.last_message_at = dbdevice.last_message_at
                dbdevice = session.merge(device)
            else:
                 dbdevice = session.add(device)
            session.commit()

            return True

        else:
            return False

    def __RestRequestBody__(self, url):

        uri = url
        params = dict(auth=self.__authkey)

        resp = requests.get(url=uri, params=params)
        data = resp.json()
        log.debug('Request to: {}'.format(resp.request.url))

        #Check Response
        if 'body' in data.keys():
            return data['body']
        else:
            log.error('Request to {} faild because {}'.format(resp.request.url, data))
            return None

    def getfolderids(self):
        """ retrieve all parsers configured """

        self.__folderids = []
        session = Session()
        query = [r for r, in session.query(Folder.id).all()]
        session.close()

        for folderid in query:

            if self.__mergefolder__(folderid):
                self.__folderids.append(folderid)
                log.debug('folder {} merged ...'.format(folderid))
            else:
                log.warning('folder {} not found in element-iot ...'.format(folderid))

        return self.__folderids

    def getparserids(self):
        """ retrieve all parsers configured """

        self.__parserids = []
        session = Session()
        query = [r for r, in session.query(Parser.id).all()]
        session.close()

        for parserid in query:

            if self.__mergeparser__(parserid):
                self.__parserids.append(parserid)
                log.debug('parser {} merged ...'.format(parserid))
            else:
                log.warning('perser {} not found in element-iot ...'.format(parserid))

        return self.__parserids

    def getdeviceids(self):
        """ retrieve all devices configured """

        self.__deviceids = []
        session = Session()
        query = [r for r, in session.query(Device.id).all()]
        session.close()

        for deviceid in query:

            if self.__mergedevice__(deviceid):
                self.__deviceids.append(deviceid)
                log.debug('device {} merged ...'.format(deviceid))
            else:
                log.warning('device {} not found in element-iot ...'.format(deviceid))

        return self.__deviceids


class ApiFolder(object):
    """
        elementiotrestapi class instances represents a FOLDER onboarded to ELEMENT IOT
        by class members you can retrieve Folder Data
    """

    def __init__(self, authkey, folderid):
        """ elementiotapi folder constructor """

        self.__authkey = authkey
        self.__folderid = folderid

        # set requerst uri s
        self.__uri_elementiotapi = 'https://element-iot.com/api/v1/tags/' + self.__folderid


        # Get Folder Instance from DB and merge it with elementiot
        self.__mergefolder__()


    def __mergefolder__(self):
        """ retreive parser representation from element-iot and merge it with db """

        # get data from elementiot
        data, _retrieve_after_id = RestRequestBody(self.__uri_elementiotapi, self.__authkey)


        # insert/merge into db
        if data:

            folder = Folder(
                            id = data['id'],
                            inserted_at = data['inserted_at'],
                            updated_at = data['updated_at'],
                            mandate_id = data['mandate_id'],
                            name = data['name'],
                            slug = data['slug'],
                            description = data['description']
                            )

            # Merge DB with element
            #
            session = Session()
            dbfolder = session.query(Folder).filter_by(id=self.__folderid).first()
            if dbfolder:
                dbfolder = session.merge(folder)

            else:
                dbfolder = session.add(folder)

            session.commit()

            self.id = folder.id
            self.inserted_at = folder.inserted_at
            self.updated_at = folder.updated_at
            self.slug = folder.slug
            self.name = folder.name
            self.description = folder.description
            self.mandate_id = folder.mandate_id

            session.close()

        else:
            self.id = None
            self.last_message_at = None
            self.inserted_at = None #: "2019-08-13T08:49:19.096588Z"
            self.updated_at = None #"2019-08-26T09:31:41.319216Z",
            self.slug = None
            self.name = None
            self.description = None
            self.mandate_id = None

    def pulldevices(self, parserids):
        """ retreive all devices from element-iot placed in this folder
            merge with db if device is in parsers
        """
        url = self.__uri_elementiotapi + '/devices'  #'https://element-iot.com/api/v1/tags/active-sensors-humidity-pro/devices'

        body, retrieve_after_id = RestRequestBody(url=url, authkey=self.__authkey)

        # loop over body
        while body:

            for data in body:

                if parserids == [] or data['parser_id'] in parserids:
                    device = ApiDevice(authkey=self.__authkey, deviceid=data['id'])
                    log.debug('Device id, timestamp: {}, {}'.format(device.id, device.inserted_at))

            body, retrieve_after_id = RestRequestBody(url=url, authkey=self.__authkey, retrieve_after_id=retrieve_after_id)


class ApiDevice(object):
    """
        elementiotrestapi class instances represents a DEVICE onboarded to ELEMENT IOT
        by class members you can retrieve Device Data, Readings and Packets measured by the Field Device
    """

    __authkey = ''
    __deviceid = ''

    __listener:threading.Thread
    __stop_event:threading.Event

    __uri_elementiotapi = 'https://element-iot.com/api/v1/devices/'
    __uri_rest_device =  ''
    __uri_rest_readings = ''

    def __init__(self, authkey, deviceid):
        """ elementiotapi constructor """

        self.__authkey = authkey
        self.__deviceid = deviceid

        # set requerst uri s
        self.__uri_rest_device = self.__uri_elementiotapi + deviceid
        self.__uri_rest_readings = self.__uri_rest_device + '/readings'

        # No Thread at constructing time
        self.__listener = None
        self.__stop_event = threading.Event()

        # Get Device Instance from DB and merge it with elementiot
        self.__mergedevice__()



    def __RestRequestBody__(self, getdevice:bool, after=''):

        if getdevice:
            uri = self.__uri_rest_device

            params = dict(
                auth=self.__authkey
            )

        else:
            uri = self.__uri_rest_readings

            params = dict(
                limit=100,
                after=after,
                sort='inserted_at',
                sort_direction='ascending',
                auth=self.__authkey
            )

        resp = requests.get(url=uri, params=params)
        data = resp.json()
        log.debug('Request to: {}'.format(resp.request.url))

        #Check Response
        if 'body' in data.keys():
            return data['body']
        else:
            log.error('Request to {} faild because {}'.format(resp.request.url, data))
            return None

    def __listen__(self, stop_event, every_second):
        """ Worker Function für listening thread """
        while not stop_event.is_set():
            time.sleep(every_second)
            log.debug('poll new messages from {} ...'.format(self.slug))
            self.getnewreadings()

    def __mergedevice__(self):
        """ Retrieve element iot device data and merge with database """

        # get data from elementiot
        data = self.__RestRequestBody__(getdevice = True)

        # insert/merge into db
        if data:
            device = Device(
                            id = data['id'],
                            inserted_at = data['inserted_at'],
                            parser_id = data['parser_id'],
                            updated_at = data['updated_at'],
                            static_location = data['static_location'],
                            slug = data['slug'],
                            name = data['name'],
                            location = data['location']

                            )

            # Merge DB with element
            #
            session = Session()
            dbdevice = session.query(Device).filter_by(id=self.__deviceid).first()
            if dbdevice:
                device.last_message_at = dbdevice.last_message_at
                dbdevice = session.merge(device)
            else:
                dbdevice = session.add(device)
            session.commit()

            self.id = device.id
            self.last_message_at = device.last_message_at
            self.inserted_at = device.inserted_at
            self.updated_at = device.updated_at
            self.static_location = device.static_location
            self.slug = device.slug
            self.name = device.name
            self.location = device.location
            self.parser_id = device.parser_id

            session.close()

        else:
            self.id = None
            self.last_message_at = None
            self.inserted_at = None #: "2019-08-13T08:49:19.096588Z"
            self.updated_at = None #"2019-08-26T09:31:41.319216Z",
            self.static_location = None #false,
            self.slug = None
            self.name = None
            self.location = None
            self.parser_id = None


    def getnewreadings(self, after = ''):
        """ retrieve all Packets after a given timestamp """

        #retrieve last packet from  device data
        if after == '':
             timestamp = self.last_message_at

             if not timestamp or timestamp == '':
                 timestamp = self.inserted_at

             log.debug('request Timestamp: {}'.format(timestamp))

        else:
            timestamp = after

        body = self.__RestRequestBody__(getdevice = False,  after=timestamp)

        # open a db session
        session = Session()

        # loop over body
        while body:

            for data in body:
                log.debug('Reading id, timestamp: {}, {}'.format(data['id'], data['inserted_at']))

                # insert Reading into Messagebuffer
                location = str(data['location']) if data['location'] != None else ''
                measurements = str(data['data'])

                message=Reading(
                    id = data['id'], # readings id
                    packet_id = data['packet_id'], # "a28000d6-18c7-4099-9bb7-976a3ece92cc",
                    device_id = data['device_id'], # "d3829df3-cb83-4691-aae8-9cf70ed85863",
                    parser_id = data['parser_id'], # "9ff236ef-e547-4f39-8494-d1fb86321c9e",
                    measured_at = data['measured_at'], # 2019-06-24T20:48:09.167897Z",
                    inserted_at = data['inserted_at'], #: "2019-08-13T08:49:19.096588Z"
                    location = location, # data['location'] if isinstance(data['location'],str) else '' , #: null,
                    data = measurements #data['data'] #: null,
                )

                try:
                    session.add(message)
                    session.commit()
                except:
                    log.error('could not ')
                    session.rollback()
                finally:
                    self.last_message_at = message.inserted_at
                    timestamp = message.inserted_at

            body = self.__RestRequestBody__(getdevice = False,  after=timestamp)

        # update db with last_message_at
        dbdevice = session.query(Device).filter_by(id=self.__deviceid).first()
        dbdevice.last_message_at = timestamp
        session.commit()
        session.close()

    def start_listening(self, poll_every_second=60):
        """ Start listening if possible
        """
        if not self.__listener:
            log.debug('start listenting {} ...'.format(self.slug))
            self.__listener = threading.Thread(target=self.__listen__, args=(self.__stop_event, poll_every_second))
            self.__listener.setDaemon(True)
            self.__listener.start()
            log.debug('worker started with thread id {}!'.format(self.__listener.ident))

        else:
            log.warning('worker listen already to {}'.format(self.slug))

    def stop_listening(self):
        """ Stop listening if possible
        """
        if self.__listener:

            self.__stop_event.set()
            self.__listener.join()
            self.__listener = None
            log.info('listening to {} stopped!'.format(self.slug))

        else:
            log.warning('no worker is listening to {} yet.'.format(self.slug))


""" Websocket Stuff TBD
# Callbacks
def on_message(ws, message):
    log.info(f'Message: {message}')

def on_error(ws, error):
    log.error(f'Error: {error}')
    ws.close()

def on_close(ws):
    log.info("### closed ###")

def on_open(ws):
    def run(*args):
        log.debug('connecting enabled...')
    thread.start_new_thread(run, ())


class elementiotapi(object):

    __authkey = ''
    __deviceid = ''
    __wss = False

    __uri_wss_packets = 'wss://element-iot.com/api/v1/devices/<deviceid>/packets/socket?auth=<authkey>'
    __uri_wss_readings = 'wss://element-iot.com/api/v1/devices/<deviceid>/readings/socket?auth=<authkey>'
    __uri_rest_device =  'https://element-iot.com/api/v1/devices/<device-id>?auth=<authkey>' # (Device Information)
    __uri_rest_packets = 'https://element-iot.com/api/v1/devices/<device-id>/packets?<params>&auth=<authkey>' #(Packets)
    __uri_rest_readings = 'https://element-iot.com/api/v1/devices/<device-id>/readings?<params>&auth=<authkey>' #(Readings)


    def __init__(self, authkey, deviceid):

        self.__authkey = authkey
        selfid = deviceid
        self.__uri_wss_packets = self.__uri_wss_packets.replace('<authkey>',authkey).replace('<deviceid>',deviceid)
        self.__uri_wss_readings = self.__uri_wss_readings.replace('<authkey>',authkey).replace('<deviceid>',deviceid)
        self.__uri_rest_device = self.__uri_rest_device.replace('<authkey>',authkey).replace('<deviceid>',deviceid)
        self.__uri_rest_packets = self.__uri_rest_packets.replace('<authkey>',authkey).replace('<deviceid>',deviceid)
        self.__uri_rest_readings = self.__uri_rest_readings.replace('<authkey>',authkey).replace('<deviceid>',deviceid)



    def OpenWebsocket(self, Endpoint=0):
        if isinstance(self.__wss, websocket.WebSocketApp):
           log.exception('can open a websocket once for a endpoint')

        else:
            websocket.enableTrace(True)
            log.info('Enabling Websocket to {}.'.format(self.__uri_wss_readings))
            self.__wss = websocket.WebSocketApp(self.__uri_wss_readings,
                                    on_message = on_message,
                                    on_error =  on_error,
                                    on_close = on_close)

            self.__wss.on_open = on_open

            self.__wss.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_interval=30, ping_timeout=10)


    def CloseWebsocket(self):
        self.__wss.close()
"""
