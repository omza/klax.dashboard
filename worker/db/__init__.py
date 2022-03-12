# imports & globals
from sqlalchemy import create_engine
from .models import Base, User
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import sessionmaker
from config import config, logging


def init_worker_db():

    # Create Database if not exists
    if not database_exists(config.MYSQL_DATABASE_URI):
        create_database(config.MYSQL_DATABASE_URI)

    # Instanciate database engine
    dbengine = create_engine(config.MYSQL_DATABASE_URI, pool_recycle=config.SQLALCHEMY_POOL_RECYCLE)

    # Bind Models to Engine, Create Models in DB if not exists
    Base.metadata.create_all(dbengine)
    # extend_existing=True

    # Instantiate an return Sessionmakerobject
    dbsession = sessionmaker(bind=dbengine)()


    # Create User
    user =  dbsession.query(User).first()
    if not user:
        user = User(firstname=config.USER_FIRSTNAME, email=config.USER_EMAIL)
        user.set_password(config.USER_PASS)
        dbsession.add(user)
        dbsession.commit()
        logging.debug(f"User {user} created")

    dbsession.close_all()

    return 
