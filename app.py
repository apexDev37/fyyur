#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# TODO: connect to a local postgresql database 
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres-admin@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
      return f'<(Venue) id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, shows: {self.shows}>'

    @hybrid_property
    def past_shows(self):
      return (
        Show.query
          .filter(Show.venue_id == self.id)
          .filter(Show.start_time < datetime.now())
          .all()
      )

    @hybrid_property
    def upcoming_shows(self):
      return (
        Show.query
          .filter(Show.venue_id == self.id)
          .filter(Show.start_time >= datetime.now())
          .all()
      )


    # TODO: implement any missing fields, as a database migration using Flask-Migrate [COMPLETED]

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String(120)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(320))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
      return f'<(Artist) id: {self.id}, name: {self.name} shows: {self.shows}>'

    @hybrid_property
    def past_shows(self):
      return (
        Show.query
          .filter(Show.artist_id == self.id)
          .filter(Show.start_time < datetime.now())
          .all()
      )

    @hybrid_property
    def upcoming_shows(self):
      return (
        Show.query
          .filter(Show.artist_id == self.id)
          .filter(Show.start_time >= datetime.now())
          .all()
      )

    # TODO: implement any missing fields, as a database migration using Flask-Migrate [COMPLETED]

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. [COMPLETED]

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<(Show) id: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id}, start_time: {self.start_time}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, datetime):
    value = value.isoformat()
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # TODO: replace with real venues data. [COMPLETED]
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  venues = db.session.query(Venue).all()
  area_groups = list({(venue.city, venue.state) for venue in venues})

  for area in area_groups:
    venues_group = [venue for venue in venues if (venue.city, venue.state) == area]
    data.append({'city': area[0], 'state': area[1], 'venues': venues_group})

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. [COMPLETED]
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')
  venues_by_search = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = {
    'count': len(venues_by_search),
    'data': [{'id': venue.id, 'name': venue.name, 'num_upcoming_shows': 0} 
              for venue in venues_by_search]    
  }

  return render_template('pages/search_venues.html', results=data, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id [COMPLETED]

  venue = db.session.query(Venue).get(venue_id)
  past_shows = venue.past_shows
  past_shows_artist_data = [
    {'artist_id': show.Artist.id, 'artist_name': show.Artist.name, 
    'artist_image_link': show.Artist.image_link, 'start_time': format_datetime(show.start_time)} 
    for show in past_shows
  ]
  upcoming_shows = venue.upcoming_shows
  upcoming_shows_artist_data = [
    {'artist_id': show.Artist.id, 'artist_name': show.Artist.name, 
    'artist_image_link': show.Artist.image_link, 'start_time': format_datetime(show.start_time)} 
    for show in upcoming_shows
  ]
  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows_artist_data,
    'upcoming_shows': upcoming_shows_artist_data,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead [COMPLETED]
  # TODO: modify data to be the data object returned from db insertion [COMPLETED] 

  error = False
  form = VenueForm(request.form)
  if form.validate():
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data
    
  try:
    new_venue = Venue(
      name=name,
      city=city, 
      state=state, 
      address=address,
      phone=phone, 
      genres=genres, 
      facebook_link=facebook_link,
      image_link=image_link, 
      website=website, 
      seeking_talent=seeking_talent,
      seeking_description=seeking_description 
    )
    print(new_venue)
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + new_venue.name + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error == True: 
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead. [Completed]
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using [COMPLETED]
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False

  try:
    venue_to_delete = db.session.query(Venue).get(venue_id)
    db.session.delete(venue_to_delete)
    db.session.commit()
    flash('Venue ' + venue_to_delete.name + ' was successfully deleted!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error == True:
      flash('An error occurred. Venue ' + venue_to_delete.name + ' could not be deleted.')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database [COMPLETED]

  artists = db.session.query(Artist).all()
  data = [{'id': artist.id, 'name': artist.name} for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. [COMPLETED]
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', '')
  artists_by_search = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = {
    'count': len(artists_by_search),
    'data': [{'id': artist.id, 'name': artist.name, 'num_upcoming_shows': 0} 
              for artist in artists_by_search]
  }

  return render_template('pages/search_artists.html', results=data, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id [COMPLETED]

  artist = db.session.query(Artist).get(artist_id)
  past_shows = artist.past_shows
  past_shows_venue_data = [
    {'venue_id': show.Venue.id, 'venue_name': show.Venue.name, 
    'venue_image_link': show.Venue.image_link, 'start_time': format_datetime(show.start_time)} 
    for show in past_shows
  ]
  upcoming_shows = artist.upcoming_shows
  upcoming_shows_venue_data = [
    {'venue_id': show.Venue.id, 'venue_name': show.Venue.name, 
    'venue_image_link': show.Venue.image_link, 'start_time': format_datetime(show.start_time)} 
    for show in upcoming_shows
  ]
  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': past_shows_venue_data,
    'upcoming_shows': upcoming_shows_venue_data,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).get(artist_id)

  # TODO: populate form with fields from artist with ID <artist_id> [COMPLETED]
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  form = ArtistForm(request.form)
  artist = db.session.query(Artist).get(artist_id)
  if form.validate():
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

  try:
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.facebook_link = facebook_link
    artist.image_link = image_link
    artist.website = website_link
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    print(artist)
    db.session.commit()
    flash(f'Artist, "{artist.name}" was successfully edited!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error == True:
      flash(f'An error occurred. Artist, "{artist.name}" could not be edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # TODO: insert form data as a new Artist record in the db, instead [COMPLETED]
  # TODO: modify data to be the data object returned from db insertion [COMPLETED]

  error = False
  form = ArtistForm(request.form)
  if form.validate():
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

  try:
    new_artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres=genres,
      facebook_link=facebook_link,
      image_link=image_link,
      website=website_link,
      seeking_venue=seeking_venue,
      seeking_description=seeking_description
    )
    print(new_artist)
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + new_artist.name + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error == True:
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')


  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead. [COMPLETED]
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real shows data. [COMPLETED]

  shows = db.session.query(Show).all()
  data = [
    {
      'venue_id': show.Venue.id, 
      'venue_name': show.Venue.name,
      'artist_id': show.Artist.id, 
      'artist_name': show.Artist.name, 
      'artist_image_link': show.Artist.image_link, 
      'start_time': format_datetime(show.start_time)
    } for show in shows
  ]  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create') 
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead [COMPLETED]

  error = False
  form = ShowForm(request.form)
  if form.validate():
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

  try:
    new_show = Show(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=start_time
    )
    print(new_show)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    error = False
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error == True:
      flash('An error occurred. Show could not be listed.')

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead. [COMPLETED]
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
