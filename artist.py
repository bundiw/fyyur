from datetime import datetime
import json
import sys
from flask import flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy import null
from forms import ArtistForm
from model import Artist, Show, Venue, app, session


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = session.query(Artist).order_by('id')

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

        past_shows_dict = session.query(Show).join(Artist).filter(
            Show.artist_id == artist.id).filter(
                str(Show.start_time) < str(datetime.now())
        ).all()

        upcomming_shows_dict = session.query(Show).join(Artist).filter(
            Show.artist_id == artist.id).filter(
                str(Show.start_time) > str(datetime.now())
        ).all()
        upcoming_shows = []
        past_shows = []
        for index in range(0, len(upcomming_shows_dict)):

            venue_id = upcomming_shows_dict[index].id
            start_time = upcomming_shows_dict[index].start_time
            venues = session.query(Venue).get(venue_id)

            venue_name = venues.name
            venue_image_link = venues.image_link

            upcoming_shows.append(
                {
                    "venue_id": venue_id,
                    "venue_name": venue_name,
                    "venue_image_link": venue_image_link,
                    "start_time": start_time
                })
        for i in range(0, len(past_shows_dict)):

            venue_id = past_shows_dict[i].venue_id
            start_time = past_shows_dict[i].start_time
            venues = session.query(Venue).get(venue_id)

            venue_name = venues.name
            venue_image_link = venues.image_link

            past_shows.append(
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

        data = list(filter(lambda d: d['id'] ==
                           artist_id, data))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(request.form)
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
    artistForm = ArtistForm()
    err_message = null
    err = False
    try:
        artist = Artist()
        artistForm.populate_obj(artist)
        db_ob_artist = session.quer(Artist).get(artist_id)
        db_ob_artist = artist
        session.add(db_ob_artist)
        session.commit()

    except ValueError as e:
        session.rollback()
        err = True
        err_message = e
        print(sys.exc_info())
    finally:
        session.close()
        if err:
            flash("Artist details could not be Editted! Error: "+err_message)
        else:

            return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm(request.form)
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    artistForm = ArtistForm()
    err_message = null
    err = False
    try:
        artist = Artist()
        artistForm.populate_obj(artist)
        session.add(artist)
        session.commit()

    except ValueError as e:
        err_message = e
        err = True
        print(sys.exc_info())
        session.rollback()

    finally:
        session.close()

        if err:
            flash('Artist could not be listed! Error: '+err_message)
        else:

            # on successful db insert, flash success
            flash('Artist ' +
                  request.form['name'] + ' was successfully listed!')
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            return render_template('pages/home.html')
