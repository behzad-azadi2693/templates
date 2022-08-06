from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean, Integer

# from sqlalchemy.orm import sessionmaker

# db_string = "postgresql://localhost:5432/boomilia_uploader_bot_db"
db_string = "postgresql://boomilia:%23BoomIlia021Mad%40@localhost:5432/boomilia_uploader_bot_db"

db = create_engine(db_string)
base = declarative_base()

Session = sessionmaker(bind=db)


class Users(base):
    __tablename__ = 'users'

    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    chat_id = Column(String, unique=True, primary_key=True)
    join_date = Column(DateTime)
    logged_in = Column(Boolean, default=False)
    token = Column(String, unique=True, nullable=True)


base.metadata.create_all(db)
