from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)