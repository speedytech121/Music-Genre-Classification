from email.policy import default
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

Base = declarative_base()
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50))
    email = Column(String(50), unique=True)
    created_on = Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.username

class Audio(Base):
    __tablename__ = 'audiofiles'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    path = Column(String(255))
    ftype = Column(String(5))
    user = Column(Integer, ForeignKey('users.id'))
    created_on = Column(DateTime, default=datetime.now)
    spath = Column(String(255),default="")
    wpath = Column(String(255),default="")
    predicted_genre = Column(String(50),nullable=True)
    predicted_confidence = Column(Float,default=0.0)

    def __str__(self):
        return self.audio_name


if __name__ == "__main__":
    engine = create_engine("sqlite:///dmb.sqlite")
    Base.metadata.create_all(engine)