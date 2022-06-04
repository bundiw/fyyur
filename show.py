import sys
from flask import flash, render_template, request
from sqlalchemy import null

from forms import ShowForm
from model import Artist, Show, Venue, app, session

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    
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

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    showform = ShowForm(request.form)
    err = False
    err_message = null
    try:
        show = Show()
        showform.populate_obj(show)
        session.add(show)
        session.commit()

    except ValueError as e:
        err = True
        err_message = e
        session.rollback()
        print(sys.exc_info())

    finally:
        session.close()
        if err:
            flash('New Show could not be listed! Error: '+err_message)

        else:
            flash('New Show listed Successfully')

            return render_template('pages/home.html')
