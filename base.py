from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///forum.db")
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)