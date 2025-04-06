from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from database import Base
from datetime import datetime

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class get_accommodations(Base): 
    __tablename__ = "accomodations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)
    total_reviews = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)  # Google API might not always provide price
    amenities = Column(JSON, nullable=True)  # Store as JSON (e.g., ["WiFi", "AC"])
    last_updated = Column(DateTime, default=datetime.utcnow)

class TransportOption(Base): 
    __tablename__ = "transport_options"
    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    transport_type = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    duration = Column(String, nullable=True)  
    distance = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
