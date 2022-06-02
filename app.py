#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import abort
import sys
from urllib import response
from xmlrpc.client import DateTime
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, session, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from forms import *
from flask_migrate import Migrate
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# Make the engine
engine = create_engine(
    "postgresql://postgres:password@localhost:5432/fyyur", future=True, echo=True)
# session = Session(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()


# Make the DeclarativeMeta
Base = declarative_base()

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(Base):
    __tablename__ = 'Shows'
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer,  ForeignKey(
        'Venues.id'))
    artist_id = Column(Integer,  ForeignKey(
        'Artists.id'))
    start_time = Column(String(), nullable=False)
    artist = relationship(
        "Artist", back_populates="venues")
    venue = relationship("Venue", back_populates="artists")


class Venue(Base):
    __tablename__ = 'Venues'

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
# Venue(name="123",city= "qdf",state=" AL",address="azxscv",phone="zxc",genres= "Blues",facebook_link= "zx",image_link="zxc",website_link= "zxc v",seeking_talent=" y",seeking_description= "zaxsc")


class Artist(Base):
    __tablename__ = 'Artists'

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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


Base.metadata.create_all(engine)
session.commit()


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    places = session.query(Venue).distinct("city", "state")
    for place in places:
        #print(place.city, place.state)
        city = place.city
        state = place.state
        venues = []
        for venue in session.query(Venue).filter_by(city=city, state=state):
            upcoming_shows = session.query(
                Show).filter_by(venue_id=venue.id).count()
            #print(type(upcoming_shows), "good")
            venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": upcoming_shows
            })
        data.append({
            "city": city,
            "state": state,
            "venues": venues
        })

    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')

    venues = session.query(Venue).filter(
        Venue.name.ilike(f'%{search_term}%'))
    venues = venues.all()

    match_count = len(venues)

    upcomming_shows_count = 0
    data = []

    for venue in venues:

        currrent_date_time = str(datetime.now())
        all_shows = session.query(Show).filter_by(venue_id=venue.id).all()

        for show in all_shows:
            if show.start_time > currrent_date_time:
                upcomming_shows_count += 1

        data.append({"id": int(venue.id),
                     "name": venue.name,
                     "num_upcoming_shows": upcomming_shows_count,
                     })
    response = {"count": int(match_count),
                "data": data}

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = []
    venues = session.query(Venue)
    for venue in venues:
        id = venue.id
        venue_id = id
        name = venue.name
        genres = venue.genres
        address = venue.address
        city = venue.city
        state = venue.state
        phone = venue.phone
        website = venue.website_link
        facebook_link = venue.facebook_link
        seeking_talent = venue.seeking_talent
        # seeking_description = venue.seeking_description
        image_link = venue.image_link
        past_shows = []
        upcoming_shows = []
        current_date_time = datetime.now()
        no_of_upcoming_shows = 0
        no_of_past_shows = 0
        shows = session.query(Show).filter_by(venue_id=id)
        for show in shows:
            artist = session.query(Artist).get(show.artist_id)
            artist_id = artist.id
            artist_name = artist.name
            artist_image_link = artist.image_link
            start_time = show.start_time
            if str(current_date_time) > start_time:
                # past show
                no_of_past_shows += 1
                past_shows.append(
                    {
                        "artist_id": artist_id,
                        "artist_name": artist_name,
                        "artist_image_link": artist_image_link,
                        "start_time": start_time
                    }
                )
            else:
                # upcomming
                no_of_upcoming_shows += 1
                upcoming_shows.append(
                    {
                        "artist_id": artist_id,
                        "artist_name": artist_name,
                        "artist_image_link": artist_image_link,
                        "start_time": start_time
                    }
                )

        data.append(
            {
                "id": id,
                "name": name,
                "genres": genres,
                "address": address,
                "city": city,
                "state": state,
                "phone": phone,
                "website": website,
                "facebook_link": facebook_link,
                "seeking_talent": seeking_talent,
                "image_link": image_link,
                "past_shows": past_shows,
                "upcoming_shows": upcoming_shows,
                "past_shows_count": no_of_past_shows,
                "upcoming_shows_count": no_of_upcoming_shows
            }

        )

        data = list(filter(lambda d: d['id'] ==
                    venue_id, data))[0]
        return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    seek_talent = False
    try:
        seek_talent = True if request.form['seeking_talent'] == 'y' else False

    except:
        seek_talent = False

    finally:
        err = False
        try:
            venue = Venue(name=request.form['name'],
                          city=request.form['city'],
                          state=request.form['state'],
                          address=request.form['address'],
                          phone=request.form['phone'],
                          genres=request.form['genres'],
                          facebook_link=request.form['facebook_link'],
                          image_link=request.form['image_link'],
                          website_link=request.form['website_link'],
                          seeking_talent=seek_talent,
                          seeking_description=request.form['seeking_description'])
            session.add(venue)
            session.commit()

        except:
            session.rollback()
            err = True
            print(sys.exc_info())

        finally:
            session.close()
            if err:
                abort()
            else:

                # on successful db insert, flash success
                flash(
                    'Venue ' + request.form['name'] + ' was successfully listed!')
                # TODO: on unsuccessful db insert, flash an error instead.
                # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
                # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
                return render_template('pages/home.html')


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # good error
    message = "success"
    try:
        session.query(Show).filter_by(venue_id=venue_id).delete()
        session.query(Venue).filter_by(id=venue_id).delete()

        session.commit()
    except:
        message = "failed"
        session.rollback()
        print(sys.exc_info())

    finally:
        session.close()
        if message != "success":
            abort()
        else:
            # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
            # clicking that button delete it from the db then redirect the user to the homepage
            return {"message": message}

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = session.query(Artist).order_by('id')
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')

    artists = session.query(Artist).filter(
        Artist.name.ilike(f'%{search_term}%'))
    artists = artists.all()

    match_count = len(artists)

    upcomming_shows_count = 0
    data = []

    for artist in artists:

        currrent_date_time = str(datetime.now())
        all_shows = session.query(Show).filter_by(artist_id=artist.id).all()

        for show in all_shows:
            if show.start_time > currrent_date_time:
                upcomming_shows_count += 1

        data.append({"id": int(artist.id),
                     "name": artist.name,
                     "num_upcoming_shows": upcomming_shows_count,
                     })
    response = {"count": int(match_count),
                "data": data}

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    data = []
    all_artists = session.query(Artist)
    for artist in all_artists:
        id = artist.id
        name = artist.name
        genres = artist.genres
        city = artist.city
        state = artist.state
        phone = artist.phone
        website = artist.website_link
        facebook_link = artist.facebook_link
        seeking_venue = artist.seeking_venue
        seeking_description = artist.seeking_description
        image_link = artist.image_link
        past_shows = []
        upcoming_shows = []
        all_shows = session.query(Show).filter(Show.artist_id == id)
        for show in all_shows:
            venue_id = show.venue_id
            start_time = show.start_time
            venues = session.query(Venue).get(venue_id)

            venue_name = venues.name
            venue_image_link = venues.image_link
            current_date_time = datetime.now()
            #print("some", current_date_time)
            if str(current_date_time) > start_time:
                past_shows.append(
                    {
                        "venue_id": venue_id,
                        "venue_name": venue_name,
                        "venue_image_link": venue_image_link,
                        "start_time": start_time
                    })

            else:
                upcoming_shows.append(
                    {
                        "venue_id": venue_id,
                        "venue_name": venue_name,
                        "venue_image_link": venue_image_link,
                        "start_time": start_time
                    })
        data.append({
            "id": id,
            "name": name,
            "genres": genres,
            "city": city,
            "state": state,
            "phone": phone,
            "website": website,
            "facebook_link": facebook_link,
            "seeking_venue": seeking_venue,
            "seeking_description": seeking_description,
            "image_link": image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows


        })
    # print(json.dumps(data))
    # [
    #     {"id": 1,
    #      "name": "asdf",
    #      "genres": "Musical Theatre",
    #      "city": "nm",
    #      "state": "AL",
    #      "phone": "m,.",
    #      "website": "kl",
    #      "facebook_link": "jkl",
    #      "seeking_venue": false,
    #      "seeking_description": "hjk",
    #      "image_link": "jkl",
    #      "past_shows": [
    #                {"venue_id": 1,
    #                 "venue_name": "asdf",
    #                 "venue_image_link": "asdf",
    #                 "start_time": "2022-05-31 17:22:17"},
    #         {"venue_id": 2,
    #                    "venue_name": "wertyu",
    #                    "venue_image_link": "fghj",
    #                    "start_time": "2022-05-31 20:43:53"
    #          }],
    #      "upcoming_shows": []}
    # ]

    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    data = list(filter(lambda d: d['id'] ==
                artist_id, data))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_obj = session.query(Artist).get(artist_id)

    artist = {
        "id":  artist_obj.id,
        "name":  artist_obj.name,
        "genres": artist_obj.genres,
        "city": artist_obj.city,
        "state": artist_obj.state,
        "phone": artist_obj.phone,
        "website": artist_obj.website_link,
        "facebook_link": artist_obj.facebook_link,
        "seeking_venue": True if artist_obj.seeking_venue == 'f' else False,
        "seeking_description": artist_obj.seeking_description,
        "image_link": artist_obj.image_link
    }
    # print(json.dumps(artist))

    # TODO: populate form with fields from artist with ID <artist_id>

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    seeking_venue = False
    try:
        seeking_venue = True if request.form['seeking_venue'] == 'y' else False,
        seeking_venue = True
    except:
        seeking_venue = False

    finally:
        err = False
        try:

            obj_artist = session.query(Artist).get(artist_id)
            obj_artist.name = request.form['name']
            obj_artist.genres = request.form['genres']
            obj_artist.city = request.form['city']
            obj_artist.state = request.form['state']
            obj_artist.phone = request.form['phone']
            obj_artist.image_link = request.form['image_link']
            obj_artist.facebook_link = request.form['facebook_link']
            obj_artist.website_link = request.form['website_link']
            obj_artist.seeking_venue = seeking_venue
            obj_artist.seeking_description = request.form['seeking_description']
            session.commit()

        except:
            err = True
            session.rollback()
            print(sys.exc_info())

        finally:
            if err:
                abort()
            else:

                return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # need toedit the venue form
    # good err
    venue = session.query(Venue).get(venue_id)

    venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "facebook_link": venue.facebook_link,
        "seeking_talent": True if venue.seeking_talent == 'f' else False,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    seek_talent = False
    err = False
    try:
        seek_talent = True if request.form['seeking_talent'] == 'y' else False

    except:

        session.rollack()
        print(sys.exc_info())

    finally:

        try:
            venues_obj = session.query(Venue).get(venue_id)

            venues_obj.name = request.form['name']
            venues_obj.city = request.form['city']
            venues_obj.state = request.form['state']
            venues_obj.address = request.form['address']
            venues_obj.phone = request.form['phone']
            venues_obj.genres = request.form['genres']
            venues_obj.facebook_link = request.form['facebook_link']
            venues_obj.image_link = request.form['image_link']
            venues_obj.website_link = request.form['website_link']
            venues_obj.facebook_link = seek_talent
            venues_obj.seeking_description = request.form['seeking_description']
            session.commit()

        except:
            err = True
            session.rollback()
            print(sys.exc_info())

        finally:
            session.close()
            if err:
                abort()
            else:

                return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    seek_venue = False
    try:
        seek_venue = True if str(
            request.form['seeking_venue']) == 'y' else False,
        seek_venue = True
    except:
        seek_venue = False

    finally:
        err = False
        try:
            artist = Artist(
                name=request.form['name'],
                city=request.form['city'],
                state=request.form['state'],
                phone=request.form['phone'],
                genres=request.form['genres'],
                facebook_link=request.form['facebook_link'],
                image_link=request.form['image_link'],
                website_link=request.form['website_link'],
                seeking_venue=seek_venue,
                seeking_description=request.form['seeking_description']

            )

            session.add(artist)
            session.commit()

        except:
            session.rollback()
            err = True
            print(sys.exc_info())

        finally:
            session.close()
            if err:
                abort()
            else:

                # on successful db insert, flash success
                flash('Artist ' +
                      request.form['name'] + ' was successfully listed!')
                # TODO: on unsuccessful db insert, flash an error instead.
                # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
                return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []
    shows = session.query(Show)
    for show in shows:
        venue_id = show.venue_id
        artist_id = show.artist_id
        start_time = show.start_time
        obj_venue = session.query(Venue).get(venue_id)
        venue_name = obj_venue.name
        obj_artist = session.query(Artist).get(artist_id)
        art_name = obj_artist.name
        artist_image_link = obj_artist.image_link
        data.append({
            "venue_id": venue_id,
            "venue_name": venue_name,
            "artist_id": artist_id,
            "artist_name": art_name,
            "artist_image_link": artist_image_link,
            "start_time": start_time
        })

    # print(data)
    # result = dbsession.query(Shares.price,
    #                          func.sum(Shares.quantity).label("Total sold")) \
    #     .filter(Shares.company == 'Google') \
    #     .group_by(Shares.price).all()
    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    err = False
    try:

        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id,
                    venue_id=venue_id,
                    start_time=start_time)

        session.add(show)
        session.commit()

    except:
        session.rollback()
        err = True
        print(sys.exc_info())

    finally:
        session.close()
        if err:
            abort()
        else:
            # on successful db insert, flash success
            flash('Show was successfully listed!')
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
