#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from enum import unique
import os
import json
import sys
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from models import *
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "UFWVS=L7D/:V1z=0BmVRF'Kqj0(eG:"


db.init_app(app)
migrate = Migrate(app, db)

# Maintain application context
ctx = app.app_context()
ctx.push()


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    # date = dateutil.parser.parse(value)
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value

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
    venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
    return render_template('pages/home.html', venues=venues, artists=artists)

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    data = []
    for location in db.session.query(Venue.city, Venue.state).\
            group_by(Venue.city, Venue.state).all():
        venues = []
        for venue in Venue.query.filter_by(state=location.state).all():
            venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": Show.query.
                filter(Show.venue_id == venue.id).count()
            })

        data.append({
            "city": location.city,
            "state": location.state,
            "venues": venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = []
    for venue in Venue.query.\
            filter(Venue.name.ilike("%{}%".format(search_term))).all():
        venues.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": Show.query.
            filter(Show.venue_id == venue.id).count()
        })
    response = {
        "count": len(venues),
        "data": venues
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=search_term
    )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = Venue.query.get(venue_id).__dict__
    data.pop('_sa_instance_state', None)

    upcoming = []
    past = []

    for show in Show.query.join(Venue).\
            filter(Venue.id == venue_id, Show.start_time <= datetime.now()).\
            all():
        past.append({
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        })

    for show in Show.query.join(Venue).\
            filter(Venue.id == venue_id, Show.start_time > datetime.now()).\
            all():
        upcoming.append({
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        })

    data['past_shows'] = past
    data['past_shows_count'] = len(past)
    data['upcoming_shows'] = upcoming
    data['upcoming_shows_count'] = len(upcoming)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if form.validate_on_submit():
        venue = Venue(name=form.name.data,
                      city=form.city.data,
                      state=form.state.data,
                      address=form.address.data,
                      phone=form.phone.data,
                      image_link=form.image_link.data,
                      genres=form.genres.data,
                      facebook_link=form.facebook_link.data,
                      website=form.website_link.data,
                      seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data)

        try:
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
            return render_template('pages/home.html')
        except Exception as e:
            flash('Failed to create venue with name ' +
                  request.form['name'] + '. Error: ' + str(e), 'error')
            print(sys.exc_info())
            return render_template('forms/new_venue.html', form=form)
    else:
        flash('Validations were not passed', 'error')
        return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    # BONUS CHALLENGE: Implement a button to delete a 
    # Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then 
    # redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = []
    for artist in Artist.query.\
            filter(Artist.name.ilike("%{}%".format(search_term))).\
            all():
        artists.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": Show.query.
            filter(Show.artist_id == artist.id).count()
        })
    response = {
        "count": len(artists),
        "data": artists
    }

    return render_template(
        'pages/search_artists.html', 
        results=response, 
        search_term=search_term
    )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.get(artist_id).__dict__
    data.pop('_sa_instance_state', None)

    upcoming = []
    past = []

    for show in Show.query.join(Venue).\
            filter(Show.artist_id == artist_id, Show.start_time <= datetime.now()).\
            all():
        past.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        })

    for show in Show.query.join(Venue).\
            filter(Show.artist_id == artist_id, Show.start_time > datetime.now()).\
            all():
        upcoming.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        })

    data['past_shows'] = past
    data['past_shows_count'] = len(past)
    data['upcoming_shows'] = upcoming
    data['upcoming_shows_count'] = len(upcoming)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()

    if form.validate_on_submit():
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.image_link = form.image_link.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        try:
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        except Exception as e:
            flash('An error occurred: ' + str(e), 'error')
            print(sys.exc_info())
            return redirect(url_for('edit_artist', artist_id=artist_id))
    else:
        msg = "Validations failed:"

        for x,y in form.errors.items(): 
            msg += x
        flash(msg)
        # flash('Validations were not passed', 'error')
        return redirect(url_for('edit_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()

    if form.validate_on_submit():
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.image_link = form.image_link.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        try:
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue_id))
        except Exception as e:
            flash('An error occurred: ' + str(e), 'error')
            print(sys.exc_info())
            return redirect(url_for('edit_venue', venue_id=venue_id))
    else:
        flash('Validations were not passed', 'error')
        return redirect(url_for('edit_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()

    if form.validate_on_submit():
        artist = Artist(name=form.name.data,
                        city=form.city.data,
                        state=form.state.data,
                        phone=form.phone.data,
                        image_link=form.image_link.data,
                        genres=form.genres.data,
                        facebook_link=form.facebook_link.data,
                        website=form.website_link.data,
                        seeking_venue=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data)

        try:
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
            return render_template('pages/home.html')
        except Exception as e:
            flash('An error occurred. Artist ' + form.name.data +
                  ' could not be listed. Error: ' + str(e))
            print(sys.exc_info())
            return render_template('forms/new_artist.html', form=form)
    else:
        flash('Validations were not passed', 'error')
        return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    data = []

    for show in Show.query.join(Artist).join(Venue).all():
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    form.artist_id.choices = [
        (el.id, el.name) for el in Artist.query.all()
    ]

    form.venue_id.choices = [
        (el.id, el.name) for el in Venue.query.all()
    ]

    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    form.artist_id.choices = [
        (el.id, el.name) for el in Artist.query.all()
    ]

    form.venue_id.choices = [
        (el.id, el.name) for el in Venue.query.all()
    ]

    if form.validate_on_submit():
        show = Show(artist_id=form.artist_id.data,
                    venue_id=form.venue_id.data,
                    start_time=form.start_time.data)

        try:
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
        except Exception as e:
            flash('An error occurred. Show could not be listed. Error: ' + str(e))
            print(sys.exc_info())
            return render_template('forms/new_venue.html', form=form)
    else:
        flash('Validations were not passed', 'error')
        return render_template('forms/new_show.html', form=form)


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
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
'''
