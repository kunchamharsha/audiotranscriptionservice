from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import literal
from sqlalchemy import and_
from sqlalchemy import desc
from models import Base
from configuration.config import DB_STRING

engine = create_engine(DB_STRING)
Base.metadata.bind = engine

def get_object():
    return sessionmaker(bind=engine)