from sqlalchemy import create_engine, ForeignKey, Column ,String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
Base = declarative_base()
engine = create_engine(f"mysql+mysqldb://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASSWORD']}@{os.environ['MYSQL_HOST']}:3306/{os.environ['MYSQL_DB']}", echo=True)
db_session = Session(engine)

class User(Base):
    __tablename__='users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

class Token(Base):
    __tablename__='tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    token = Column(String(500), unique=True, nullable=False)

class Video(Base):
    __tablename__='videos'
    id = Column(String(500), primary_key=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)

class Vl(Base):
    __tablename__='vls'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    
def create_tables():
    Base.metadata.create_all(engine)