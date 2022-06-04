from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
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
    name = db.Column(db.String, nullable=False, unique=True)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
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
