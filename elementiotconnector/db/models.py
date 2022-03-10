# imports & globals
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base


# Models
Base = declarative_base()

# Devices
class Device(Base):
    __tablename__ = 'devices'
    
    id = Column(String(40), primary_key=True) #*
    parser_id = Column(String(40)) #68fb21ff-436c-4ba1-8eba-4ece5b6cc6e9
    last_message_at = Column(String(28))
    inserted_at = Column(String(28)) #: 2019-08-13T08:49:19.096588Z    
    updated_at = Column(String(28)) #2019-08-26T09:31:41.319216Z,
    static_location = Column(Boolean) #false,
    slug = Column(String(255)) #: speedfreak-martinfeld,
    name = Column(String(255)) #Speed-o-mat Martinfeld,
    location = Column(JSON) #: null,



# Readings
class Reading(Base):
    __tablename__ = 'readings'
    
    id = Column(String(40), primary_key=True) # readings id ***
    packet_id = Column(String(40)) # a28000d6-18c7-4099-9bb7-976a3ece92cc,    
    device_id = Column(String(40)) # d3829df3-cb83-4691-aae8-9cf70ed85863,    
    parser_id = Column(String(40)) # 9ff236ef-e547-4f39-8494-d1fb86321c9e,
    measured_at = Column(String(28)) # 2019-06-24T20:48:09.167897Z,
    inserted_at = Column(String(28)) #: 2019-08-13T08:49:19.096588Z   
    location = Column(String(512)) #: null,
    data = Column(String(4096)) #: null, 




class Folder(Base):
    __tablename__ = 'folder'
    
    id = Column(String(40), primary_key=True) # readings id ***
    mandate_id = Column(String(40)) # readings id ***    
    inserted_at = Column(String(28)) #: 2019-08-13T08:49:19.096588Z   
    updated_at = Column(String(28)) #2019-08-26T09:31:41.319216Z,
    slug = Column(String(255)) #: speedfreak-martinfeld,
    name = Column(String(255)) #Speed-o-mat Martinfeld,
    description = Column(String(4096)) #: null, 



class Parser(Base):
    __tablename__ = 'parser'
    
    id = Column(String(40), primary_key=True) # readings id ***
    mandate_id = Column(String(40)) # readings id ***    
    inserted_at = Column(String(28)) #: 2019-08-13T08:49:19.096588Z   
    updated_at = Column(String(28)) #2019-08-26T09:31:41.319216Z,
    name = Column(String(255)) #Speed-o-mat Martinfeld,  


class Apikey(Base):
    __tablename__ = 'apikeys' 

    id = Column(String(40), primary_key=True) # readings id ***
    valid_until = Column(String(28)) #2020-08-22T08:50:07.659000Z,
    updated_at = Column(String(28)) # 2019-08-22T08  #50:20.292731Z,
    role = Column(String(255)) # admin,
    rate_scale = Column(Integer) # 10000,
    rate_limit = Column(Integer) # 50,
    name = Column(String(255)) # Speedfreak,
    mandate_id = Column(String(40)) # 15290f40-459e-4c0a-80f9-b106cd406618,
    key = Column(String(40)) # 
    inserted_at = Column(String(28)) # 2019-08-22T08:50:20.292731Z,