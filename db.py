from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///blood_pressure.db')

db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    systolic = Column(Integer)
    diastolic = Column(Integer)


def init_db():
    Base.metadata.create_all(bind=engine)
