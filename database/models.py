from sqlalchemy import Column, Integer, Float, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    country = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    price_range = Column(String, nullable=True)
    amenities = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    rating = Column(String, nullable=True)
    contact = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    embedding = Column(String, nullable=True)  # stored as text like "[0.12, 0.34, ...]"

def create_tables(engine):
    Base.metadata.create_all(engine)
    print("[db] Tables created / verified")