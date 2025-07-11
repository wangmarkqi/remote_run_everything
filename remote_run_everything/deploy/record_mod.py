from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

from sqlalchemy import Integer, DECIMAL, DateTime, Index, Integer, String, Column, Text
import json, arrow, sys, os


class Base(DeclarativeBase):
    pass


class Up(Base):
    __tablename__ = 'up'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    host = Column(String(50), default="")
    path = Column(String(50), default="")
    time = Column(String(50), default="")


class Down(Base):
    __tablename__ = 'down'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    path = Column(String(50), default="")
    time = Column(String(50), default="")


