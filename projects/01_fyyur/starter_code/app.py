#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show
import sys
import re

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
# Local postgres URI provided in config.py
# Connection is established with local database fyyurdb
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Please see models.py - In the interest of Seperation of Concerns!
# Import is done above

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # Group venues by city and state, filter by city and state, fetch ID and Name of the venue
  venue_data = []
  city_state_group = Venue.query.with_entities(Venue.city, Venue.state).group_by(
    Venue.city, Venue.state).all()

  for city, state in city_state_group:
    venue = Venue.query.with_entities(Venue.id, Venue.name).filter_by(
      city=city, state=state).order_by('id').all()
    
    # print(venue)
    
    venue_data.append({
      'city': city,
      'state': state,
      'venues': venue,
    })

  # print(venue_data)

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=venue_data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # Filter the artist table and fetch the artist requested
  venue_data = Venue.query.get(venue_id)
  show_venue_data = {}
  error = False

  if venue_data is None: # If the Artist does not exist, flash and error message
    return render_template('errors/404.html'), 404
  else: # If artist exist, now get shows related to artist and deduce upcoming and past shows
    try:
      # Get the shows. Initialise containers for counting past and upcoming show, utilise relationship
      shows_data = venue_data.shows
      show_venue_data['upcoming_shows'] = []
      show_venue_data['past_shows']= []
      show_venue_data['upcoming_shows_count'] = 0
      show_venue_data['past_shows_count'] = 0

      # For all shows...
      for show in shows_data:
        show.artist_name = show.artist.name
        show.artist_image_link = show.artist.image_link
        if show.start_time > datetime.now(): # In the future...
          show.start_time = format_datetime(str(show.start_time))
          show_venue_data['upcoming_shows'].append(show)
          show_venue_data['upcoming_shows_count'] += 1
        else: # Past...
          show.start_time = format_datetime(str(show.start_time))
          show_venue_data['past_shows'].append(show)
          show_venue_data['past_shows_count'] += 1

      # Now construct the rest of the data that is straight forward
      show_venue_data['id'] = venue_data.id
      show_venue_data['name'] = venue_data.name
      show_venue_data['genres'] = venue_data.genres.split(',')
      show_venue_data['address'] = venue_data.address
      show_venue_data['city'] = venue_data.city
      show_venue_data['state'] = venue_data.state
      show_venue_data['phone'] = venue_data.phone
      show_venue_data['website'] = venue_data.website_link
      show_venue_data['facebook_link'] = venue_data.facebook_link
      show_venue_data['seeking_talent'] = venue_data.seeking_talent
      show_venue_data['seeking_description'] = venue_data.seeking_description
      show_venue_data['image_link'] = venue_data.image_link
    except:
      error = True
    if error:
      return render_template('errors/500.html'), 500
    else:
      return render_template('pages/show_venue.html', venue=show_venue_data)

  # return render_template('pages/show_venue.html', venue=show_venue_data)

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  # return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  incoming_venue_data = VenueForm(request.form)
  error = False

  try:
    # Modify genres data to suit database object
    # join incoming list with elements with a "*"
    join_delimeter = '*'
    joined_genres_list = join_delimeter.join(incoming_venue_data.genres.data)
    # Use regex to replace special characters with ', ' to match what we need "a, b, c"
    special_characters = '[^A-Za-z0-9*]'
    genres = re.sub(special_characters, '', joined_genres_list).replace(join_delimeter, ', ')
    # Creating the Venue model from incoming form data 
    new_venue_data = Venue(
      name = incoming_venue_data.name.data,
      city = incoming_venue_data.city.data,
      state = incoming_venue_data.state.data,
      address = incoming_venue_data.address.data,
      phone = incoming_venue_data.phone.data,
      image_link = incoming_venue_data.image_link.data,
      facebook_link = incoming_venue_data.facebook_link.data,
      website_link = incoming_venue_data.website_link.data,
      genres = genres,
      seeking_talent = incoming_venue_data.seeking_talent.data,
      seeking_description = incoming_venue_data.seeking_description.data,
    )
    # Now add and commit Venue table to the database so that we are using real data
    db.session.add(new_venue_data)
    db.session.commit()
  except:
    # Activate error flag and roll back changes to the database
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # Now close database session
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed!')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # Extract ALL IDs and names of of artists from the model, order by ID 
  artist_data = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()
  # print(artist_data)
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=artist_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  # Filter the artist table and fetch the artist requested
  artist_data = Artist.query.get(artist_id)
  show_artist_data = {}
  error = False

  if artist_data is None: # If the Artist does not exist, flash and error message
    return render_template('errors/404.html'), 404
  else: # If artist exist, now get shows related to artist and deduce upcoming and past shows
    try:
      # Get the shows. Initialise containers for counting past and upcoming show
      shows_data = artist_data.shows
      show_artist_data['upcoming_shows'] = []
      show_artist_data['past_shows']= []
      show_artist_data['upcoming_shows_count'] = 0
      show_artist_data['past_shows_count'] = 0

      # For all shows...
      for show in shows_data:
        #show.id = show.venue.id
        show.venue_name = show.venue.name
        show.venue_image_link = show.venue.image_link
        if show.start_time > datetime.now(): # In the future...
          show.start_time = format_datetime(str(show.start_time))
          show_artist_data['upcoming_shows'].append(show)
          show_artist_data['upcoming_shows_count'] += 1
        else: # Past...
          show.start_time = format_datetime(str(show.start_time))
          show_artist_data['past_shows'].append(show)
          show_artist_data['past_shows_count'] += 1

      # Now construct the rest of the data that is straight forward
      show_artist_data['id'] = artist_data.id
      show_artist_data['name'] = artist_data.name
      show_artist_data['genres'] = artist_data.genres.split(',')
      show_artist_data['city'] = artist_data.city
      show_artist_data['state'] = artist_data.state
      show_artist_data['phone'] = artist_data.phone
      show_artist_data['website'] = artist_data.website_link
      show_artist_data['facebook_link'] = artist_data.facebook_link
      show_artist_data['seeking_venue'] = artist_data.seeking_venue
      show_artist_data['seeking_description'] = artist_data.seeking_description
      show_artist_data['image_link'] = artist_data.image_link
    except:
      error = True
    if error:
      return render_template('errors/500.html'), 500
    else:
      return render_template('pages/show_artist.html', artist=show_artist_data)
  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  # return render_template('forms/edit_artist.html', form=form, artist=current_artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)

  # Modify genres data to suit database object
  # join incoming list with elements with a "*"
  join_delimeter = '*'
  joined_genres_list = join_delimeter.join(form.genres.data)
  # Use regex to replace special characters with ', ' to match what we need "a, b, c"
  special_characters = '[^A-Za-z0-9&*]'
  genres = re.sub(special_characters, '', joined_genres_list).replace(join_delimeter, ', ')

  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = genres
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    flash(f'Artist {form.name.data} was successfully edited!')
  except ValueError as e:
    db.session.rollback()
    flash(f'An error occurred in {form.name.data}. Error: {str(e)}')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

  # form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # # TODO: populate form with values from venue with ID <venue_id>
  # return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)

  # Modify genres data to suit database object
  # join incoming list with elements with a "*"
  join_delimeter = '*'
  joined_genres_list = join_delimeter.join(form.genres.data)
  # Use regex to replace special characters with ', ' to match what we need "a, b, c"
  special_characters = '[^A-Za-z0-9&*]'
  genres = re.sub(special_characters, '', joined_genres_list).replace(join_delimeter, ', ')

  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.genres = genres
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    flash(f'Venue {form.name.data} was successfully edited!')
  except ValueError as e:
    db.session.rollback()
    flash(f'An error occurred in {form.name.data}. Error: {str(e)}')
  finally:
    db.session.close()
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
  incoming_artist_data = ArtistForm(request.form)
  error = False

  try:
    # Modify genres data to suit database object
    # join incoming list with elements with a "*"
    join_delimeter = '*'
    joined_genres_list = join_delimeter.join(incoming_artist_data.genres.data)
    # Use regex to replace special characters with ', ' to match what we need "a, b, c"
    special_characters = '[^A-Za-z0-9&*]'
    genres = re.sub(special_characters, '', joined_genres_list).replace(join_delimeter, ', ')

    # Creating new artist model to provide real data
    new_artist_data = Artist(
      name = incoming_artist_data.name.data,
      city = incoming_artist_data.city.data,
      state = incoming_artist_data.state.data,
      phone = incoming_artist_data.phone.data,
      genres =  genres, #incoming_artist_data.genres.data,
      image_link = incoming_artist_data.image_link.data,
      facebook_link = incoming_artist_data.facebook_link.data,
      website_link = incoming_artist_data.website_link.data,
      seeking_venue = incoming_artist_data.seeking_venue.data,
      seeking_description = incoming_artist_data.seeking_description.data
    )
    # Add and commit artist table data to database
    db.session.add(new_artist_data)
    db.session.commit()
  except:
    # If there are any errors, rollback changes
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + incoming_artist_data.name.data + ' could not be listed!')
  else:
    # on successful db insert, flash success
    flash('Artist ' + incoming_artist_data.name.data + ' was successfully listed!')

  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # Get all the data from show model, order them by earliest start time
  # Use relationship built into models to extract venue and artist information
  # This is where the backref comes into play
  show_data = Show.query.order_by('start_time').all()
  # print(show_data)
  new_show_data = []
  for show in show_data:
    # Creating and assigning show details in the structure required
    show.venue_id = show.venue.id
    show.venue_name = show.venue.name
    show.artist_id = show.artist.id
    show.artist_name = show.artist.name
    show.artist_image = show.artist.image_link
    show.start_time = format_datetime(str(show.start_time))

    # Append the show detail into the overall container that will list all shows
    new_show_data.append(show)
  # print(new_show_data)

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=new_show_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  incoming_show_data = ShowForm(request.form)
  error = False

  try:
    # Creating new show model based on form input
    new_show_data = Show(
      venue_id = incoming_show_data.venue_id.data,
      artist_id = incoming_show_data.artist_id.data,
      start_time = incoming_show_data.start_time.data
    )
    # Adding and commiting to database
    db.session.add(new_show_data)
    db.session.commit()
  except:
    # If errors occur, roll back changes to database
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  return redirect(url_for('index'))

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
