from sqlalchemy import Column, Integer, String
from database import Base

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True)
    base_id = Column(Integer)
    asset_id = Column(Integer)
    quantity = Column(Integer)

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True)
    from_base = Column(Integer)
    to_base = Column(Integer)
    asset_id = Column(Integer)
    quantity = Column(Integer)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    base_id = Column(Integer)
    asset_id = Column(Integer)
    assigned_to = Column(String)
    quantity = Column(Integer)

class Expenditure(Base):
    __tablename__ = "expenditures"
    id = Column(Integer, primary_key=True)
    base_id = Column(Integer)
    asset_id = Column(Integer)
    quantity = Column(Integer)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    base_id = Column(Integer)

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    action = Column(String)
    details = Column(String)