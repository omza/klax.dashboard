# imports & globals
from config import config, log

from sqlalchemy import create_engine
from .models import Base
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import sessionmaker

# Create Database if not exists
if not database_exists(config.MYSQL_DATABASE_URI):
    create_database(config.MYSQL_DATABASE_URI)

# Instanciate database engine
dbengine = create_engine(config.MYSQL_DATABASE_URI, pool_recycle=config.SQLALCHEMY_POOL_RECYCLE)

# Bind Models to Engine, Create Models in DB if not exists
Base.metadata.create_all(dbengine)

Session = sessionmaker(bind=dbengine)
