#----------------------------------------------------------------------------#
# Imports.
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#----------------------------------------------------------------------------#
# Config.
#----------------------------------------------------------------------------#
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    genres = db.Column('genres', db.ARRAY(db.String()), nullable=False)   # Type defined as ARRAY because venues can host multiple genres
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue ID: {self.id}, Name: {self.name}, City: {self.city}, Phone: {self.phone}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # Website link, genres, seeking talent, seeking description and shows were missing.
    # Fields defined above

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)
  
    def __repr__(self):
      return f'<Artist ID: {self.id}, Name: {self.name}, Phone: {self.phone}, Seeking: {self.seeking_venue}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # Website link, seeking venue, seeking description and shows were missing.
    # Fields defined above

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  def __repr__(self):
    return f'<Show ID: {self.id}, Venue ID: {self.venue_id}, Artist ID: {self.artist_id}, TD: {self.start_time}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# Class created above - ID, venue ID, artist ID and start time defined above
# Dunder repr method implemented for debug and easy visuals
