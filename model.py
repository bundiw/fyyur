# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# import os

from unittest.mock import Base
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker

# Make the DeclarativeMeta

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
Migrate(app, db)

Base = declarative_base()

engine = create_engine('postgresql://postgres:password@localhost:5432/fyyur')
# session = Session(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# # Models.
# #----------------------------------------------------------------------------#

# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(Base):
    __tablename__ = 'shows'
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer,  ForeignKey(
        'venues.id'))
    artist_id = Column(Integer,  ForeignKey(
        'artists.id'))
    start_time = Column(String(), nullable=False)
    artist = relationship(
        "Artist", back_populates="venues")
    venue = relationship("Venue", back_populates="artists")


class Venue(Base):
    __tablename__ = 'venues'

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    address = Column(String(120), nullable=False)
    phone = Column(String(120), nullable=False)
    genres = Column(String(120), nullable=False)
    image_link = Column(String(600), nullable=False)
    facebook_link = Column(String(120), nullable=False)
    website_link = Column(String(120), nullable=False)
    seeking_talent = Column(Boolean(), default=False)
    seeking_description = Column(String(300), nullable=False)
    artists = relationship("Show",
                           back_populates="venue", lazy="dynamic")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(Base):
    __tablename__ = 'artists'

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    phone = Column(String(120), nullable=False)
    genres = Column(String(120), nullable=False)
    image_link = Column(String(600), nullable=False)
    facebook_link = Column(String(120), nullable=False)
    website_link = Column(String(120), nullable=False)
    seeking_venue = Column(Boolean, default=False)
    seeking_description = Column(String(300), nullable=False)
    venues = relationship(
        "Show", back_populates="artist", lazy="dynamic")


Base.metadata.create_all(engine)
