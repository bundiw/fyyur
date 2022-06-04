from datetime import datetime
import json
import sys
from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import null

from forms import VenueForm

from model import Show, Venue, app, session


#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    data = []
    places = session.query(Venue).distinct("city", "state")
    for place in places:
        # print(place.city, place.state)
        city = place.city
        state = place.state
        venues = []
        for venue in session.query(Venue).filter_by(city=city, state=state):
            upcoming_shows = session.query(
                Show).filter_by(venue_id=venue.id).count()
            # print(type(upcoming_shows), "good")
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

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get('search_term', '')

    venues = session.query(Venue).filter(
        Venue.name.ilike(f'%{search_term}%'))
    venues = venues.all()

    match_count = len(venues)

    upcomming_shows_count = 0

    data = []
    for venue in venues:
        upcomming_shows_count = len(session.query(Show).join(Venue).filter(
            Show.venue_id == venue.id).filter(str(Show.start_time) > str(datetime.now())).all())

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

    venue = session.query(
        Venue
    ).get(venue_id)
    data = []
    past_shows_count = len(session.query(Show).join(Venue).filter(
        Show.artist_id == venue.id).filter(str(Show.start_time) < str(datetime.now())).all())
    upcoming_shows_count = len(session.query(Show).join(Venue).filter(
        Show.venue_id == venue.id).filter(str(Show.start_time) > str(datetime.now())).all())
    id = venue.id
    data.append({
        "id": id,
        "name": venue.name,
        "genres": venue.genres,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
        "address": venue.address,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count

    })

    data = list(filter(lambda d: d['id'] ==
                       venue_id, data))[0]
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    venueform = VenueForm(request.form)
    err = False
    err_message = null
    try:

        venue = Venue()
        venueform.populate_obj(venue)
        session.add(venue)
        session.commit()

    except ValueError as e:
        session.rollback()
        err = True
        err_message = e
        print(sys.exc_info())

    finally:
        session.close()
        if err:
            flash('Venue could not be listed! Error: '+err_message)

        else:
            flash(
                'Venue ' + request.form['name'] + ' was successfully listed!')

            return render_template('pages/home.html')


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    message = "success"
    err_message = null
    try:
        session.query(Show).filter_by(venue_id=venue_id).delete()
        session.query(Venue).filter_by(id=venue_id).delete()

        session.commit()
    except ValueError as e:
        message = "failed"
        session.rollback()
        err_message = e
        print(sys.exc_info())

    finally:
        session.close()
        if message != "success":
            flash(
                'Venue could not delete! Error: '+err_message)

        else:
            return {"message": message}


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm(request.form)
    ob_venue = session.query(Venue).get(venue_id)

    # need toedit the venue form
    err_message = null
    err = False
    data = {}
    try:

        data = {
            "id": ob_venue.id,
            "name": ob_venue.name,
            "genres": ob_venue.genres,
            "address": ob_venue.address,
            "city": ob_venue.city,
            "state": ob_venue.state,
            "facebook_link": ob_venue.facebook_link,
            "seeking_talent": True if ob_venue.seeking_talent == 'f' else False,
            "seeking_description": ob_venue.seeking_description,
            "image_link": ob_venue.image_link
        }

    except ValueError as e:
        err_message = e
        err = True
        print(sys.exc_info())

    finally:
        if err:
            flash('Error was encountered! Error:' + err_message)
            return redirect(url_for('not_found_error'))

        else:
            venue = data

            return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venueForm = VenueForm(request.form)
    err_message = null
    err = False

    seek_talent = False
    try:
        seek_talent = True if request.form['seeking_talent'] == 'y' else False

    except:
        pass

    finally:

        try:

            venue = Venue()
            db_venue = session.query(Venue).get(venue_id)
            venueForm.populate_obj(venue)
            db_venue.name = venue.name
            db_venue.city = venue.city
            db_venue.state = venue.state
            db_venue.address = venue.address
            db_venue.phone = venue.phone
            db_venue.genres = venue.genres
            db_venue.facebook_link = venue.facebook_link
            db_venue.image_link = venue.image_link
            db_venue.website_link = venue.website_link
            db_venue.seeking_talent = seek_talent
            db_venue.seeking_description = venue.seeking_description

            session.commit()

        except ValueError as e:
            err = True
            err_message = e
            print(err_message)
            session.rollback()

        finally:
            session.close()
            if err:
                flash('Venue Details could not be edited '+err_message)
                return redirect(url_for('not_found_error'))
            else:
                flash('Venue Details edited  successfully')

                return redirect(url_for('show_venue', venue_id=venue_id))
